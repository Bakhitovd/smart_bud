import openai
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

class FileProcessor:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def extract_transactions(self, file_content: str, filename: str) -> List[Dict[str, Any]]:
        """
        Extract transactions from any file format using LLM
        """
        prompt = f"""
        Extract all financial transactions from this file content. The file may be CSV, TXT, PDF text, or any format.
        
        File name: {filename}
        File content:
        {file_content}
        
        Return a JSON array with transactions in this exact format:
        [
            {{
                "date": "YYYY-MM-DD",
                "amount": -123.45,
                "description": "MERCHANT NAME OR DESCRIPTION",
                "account_info": "any additional account details if available"
            }}
        ]
        
        Rules:
        - Use negative amounts for expenses/debits, positive for income/credits
        - Parse dates to YYYY-MM-DD format
        - Clean up merchant names and descriptions
        - If you cannot extract clear transactions, return an empty array []
        - Only return valid JSON, no explanations
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial data extraction expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            result = response.choices[0].message.content.strip()
            
            # Try to parse the JSON response
            try:
                transactions = json.loads(result)
                if not isinstance(transactions, list):
                    return []
                
                # Validate and clean each transaction
                cleaned_transactions = []
                for trans in transactions:
                    if self._validate_transaction(trans):
                        cleaned_transactions.append(self._clean_transaction(trans))
                
                return cleaned_transactions
                
            except json.JSONDecodeError:
                print(f"Failed to parse LLM response as JSON: {result}")
                return []
                
        except Exception as e:
            print(f"Error extracting transactions: {str(e)}")
            return []
    
    def _validate_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Validate that transaction has required fields"""
        required_fields = ["date", "amount", "description"]
        return all(field in transaction for field in required_fields)
    
    def _clean_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and standardize transaction data"""
        try:
            # Parse date
            date_str = transaction["date"]
            if isinstance(date_str, str):
                # Try different date formats
                for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%Y/%m/%d"]:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    # If no format works, use current date
                    parsed_date = datetime.now()
            else:
                parsed_date = datetime.now()
            
            return {
                "date": parsed_date.isoformat(),
                "amount": float(transaction["amount"]),
                "description": str(transaction["description"]).strip(),
                "account_info": transaction.get("account_info", "")
            }
        except Exception as e:
            print(f"Error cleaning transaction: {str(e)}")
            return None
    
    def detect_file_format(self, content: str, filename: str) -> str:
        """Detect the file format for better processing"""
        if filename.lower().endswith('.csv'):
            return "CSV"
        elif filename.lower().endswith('.txt'):
            return "TXT"
        elif filename.lower().endswith('.pdf'):
            return "PDF"
        else:
            return "UNKNOWN"
