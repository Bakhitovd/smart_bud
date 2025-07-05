import openai
import json
import os
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

class TransactionCategorizer:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def categorize_transaction(self, description: str, amount: float, categories: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Categorize a single transaction using LLM
        """
        category_list = [cat["name"] for cat in categories]
        
        prompt = f"""
        Categorize this financial transaction:
        
        Description: "{description}"
        Amount: ${abs(amount):.2f}
        
        Available categories: {', '.join(category_list)}
        
        Return JSON in this exact format:
        {{
            "category": "category_name",
            "confidence": 0.95,
            "reasoning": "brief explanation why this category fits"
        }}
        
        Rules:
        - Choose the most appropriate category from the available list
        - Confidence should be 0.0 to 1.0 (1.0 = completely certain)
        - If confidence is below 0.7, the transaction will need manual review
        - Use "Other" if no category fits well
        - Only return valid JSON, no explanations
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial categorization expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            result = response.choices[0].message.content.strip()
            
            try:
                categorization = json.loads(result)
                
                # Validate the response
                if not all(key in categorization for key in ["category", "confidence", "reasoning"]):
                    return self._fallback_categorization()
                
                # Ensure category exists in our list
                if categorization["category"] not in category_list:
                    categorization["category"] = "Other"
                    categorization["confidence"] = 0.5
                    categorization["reasoning"] = "Category not found in available options"
                
                # Ensure confidence is a valid float
                try:
                    categorization["confidence"] = float(categorization["confidence"])
                    if not 0.0 <= categorization["confidence"] <= 1.0:
                        categorization["confidence"] = 0.5
                except (ValueError, TypeError):
                    categorization["confidence"] = 0.5
                
                return categorization
                
            except json.JSONDecodeError:
                print(f"Failed to parse categorization response: {result}")
                return self._fallback_categorization()
                
        except Exception as e:
            print(f"Error categorizing transaction: {str(e)}")
            return self._fallback_categorization()
    
    async def categorize_batch(self, transactions: List[Dict[str, Any]], categories: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Categorize multiple transactions in batch
        """
        categorized_transactions = []
        
        for transaction in transactions:
            categorization = await self.categorize_transaction(
                transaction["description"],
                transaction["amount"],
                categories
            )
            
            # Add categorization info to transaction
            transaction.update({
                "category_name": categorization["category"],
                "confidence_score": categorization["confidence"],
                "needs_review": categorization["confidence"] < 0.7,
                "reasoning": categorization["reasoning"]
            })
            
            categorized_transactions.append(transaction)
        
        return categorized_transactions
    
    def _fallback_categorization(self) -> Dict[str, Any]:
        """Fallback categorization when LLM fails"""
        return {
            "category": "Other",
            "confidence": 0.0,
            "reasoning": "Failed to categorize automatically"
        }
    
    def get_category_id_by_name(self, category_name: str, categories: List[Dict[str, Any]]) -> int:
        """Get category ID by name"""
        for cat in categories:
            if cat["name"] == category_name:
                return cat["id"]
        
        # Return "Other" category ID if not found
        for cat in categories:
            if cat["name"] == "Other":
                return cat["id"]
        
        return None
