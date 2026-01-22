"""
RAG Chatbot using Groq API (Fast & Free)
Retrieves relevant context and generates responses
"""

import os
from typing import List, Dict
from dotenv import load_dotenv
from groq import Groq
from .vector_store import VectorStoreManager

load_dotenv()


class RAGChatbot:
    """RAG-based chatbot for Aadhaar data queries using Groq"""
    
    def __init__(self):
        self.vector_store = VectorStoreManager()
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.llm_model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        
        # Initialize Groq client
        if self.groq_api_key and self.groq_api_key != "your_groq_api_key_here":
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
                self.use_groq = True
                print(f"✓ Using Groq with model: {self.llm_model}")
            except Exception as e:
                 print(f"Error initializing Groq: {e}")
                 self.use_groq = False
        else:
            self.use_groq = False
            print("⚠ Warning: Groq API key not set. Using template-based responses.")
    
    def retrieve_context(self, query: str, top_k: int = 3) -> List[Dict]:
        """Retrieve relevant context from vector store"""
        return self.vector_store.search(query, top_k=top_k)
    
    def format_context(self, results: List[Dict]) -> str:
        """Format retrieved results into context string"""
        context_parts = []
        
        for idx, result in enumerate(results, 1):
            context_parts.append(f"--- Context {idx} (Relevance: {result['score']:.3f}) ---")
            context_parts.append(f"Source: {result['metadata']['source']}")
            context_parts.append(f"Data Type: {result['metadata']['data_type']}")
            context_parts.append(f"\n{result['text'][:1500]}")  # Include more text for better context
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def generate_response_groq(self, query: str, context: str) -> str:
        """Generate response using Groq API (fast & free)"""
        
        system_prompt = """You are an intelligent AI assistant specialized in analyzing Indian Aadhaar enrollment data. 
You have access to comprehensive datasets including:
1. General Aadhaar enrollment statistics
2. Demographic monthly updates
3. Biometric updates

Your role is to:
1. Analyze the provided context data accurately and thoroughly
2. Answer questions about Aadhaar enrollment statistics, trends, and patterns
3. Provide insights based on the numerical data in the context
4. Be precise with numbers, dates, states, districts, and statistics
5. Compare data across different regions, time periods, or categories when relevant
6. Clearly state if the context doesn't contain enough information to fully answer the question

IMPORTANT: 
- Always base your answers strictly on the provided context
- Quote specific numbers and statistics from the context
- Mention which data source the information comes from
- If data is missing or unclear, acknowledge this limitation
- Be conversational and helpful in your responses"""

        user_prompt = f"""Based on the following context from the Aadhaar enrollment database, please answer the user's question.

CONTEXT FROM AADHAAR DATABASE:
{context}

USER QUESTION: {query}

Please provide a clear, accurate, and detailed answer based on the context above. Include specific numbers, 
statistics, and trends from the data. Cite which data source you're referencing."""

        try:
            # Use Groq Chat Completion API
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                model=self.llm_model,
                temperature=0.3,  # Lower for more factual responses
                max_tokens=1024,
                top_p=0.9,
            )
            
            return chat_completion.choices[0].message.content
        
        except Exception as e:
            return f"Error generating response with Groq: {str(e)}\n\nPlease check your Groq API key and try again."
    
    def generate_response_template(self, query: str, context: str) -> str:
        """Generate a simple template-based response (fallback)"""
        
        response = f"""Based on the Aadhaar enrollment data, here's the relevant information I found:

{context}

---
📝 Note: To get AI-powered intelligent responses, please add your Groq API key to the .env file.
Groq provides fast, free access to powerful LLMs like Llama 3.3!
"""
        return response
    
    def chat(self, query: str, top_k: int = 3) -> Dict[str, any]:
        """Main chat interface"""
        
        print(f"\nQuery: {query}")
        print("Retrieving relevant context from all datasets...")
        
        # Retrieve context from vector database
        results = self.retrieve_context(query, top_k=top_k)
        
        if not results:
            return {
                "query": query,
                "response": "I couldn't find any relevant information in the Aadhaar database for your query. Please try rephrasing your question or ask about specific states, districts, enrollment numbers, or demographic/biometric updates.",
                "sources": []
            }
        
        # Format context
        context = self.format_context(results)
        
        print("Generating AI-powered response...")
        
        # Generate response
        if self.use_groq:
            response = self.generate_response_groq(query, context)
        else:
            response = self.generate_response_template(query, context)
        
        # Prepare source information
        sources = [
            {
                "source": r["metadata"]["source"],
                "data_type": r["metadata"]["data_type"],
                "relevance": r["score"]
            }
            for r in results
        ]
        
        return {
            "query": query,
            "response": response,
            "sources": sources,
            "context": context
        }
