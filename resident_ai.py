import os
import json
from groq import Groq
from memory import TradeMemory
import config

class ResidentAI:
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.client = None
        self.memory = TradeMemory()
        
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                print("🧠 Resident AI: Connected to Groq")
            except Exception as e:
                print(f"⚠️ Resident AI Error: {e}")
        else:
            print("⚠️ Resident AI: No GROQ_API_KEY found. AI features disabled.")

    def chat(self, user_message: str, context: dict = None) -> str:
        """
        Chat with the Resident AI.
        """
        if not self.client:
            return "I'm sorry, my brain isn't connected yet. Please set the GROQ_API_KEY."

        # Get recent lessons
        lessons = self.memory.get_relevant_lessons()
        lessons_text = "\n".join([f"- {l}" for l in lessons]) if lessons else "No specific lessons yet."

        system_prompt = f"""You are the Resident AI for the APEX TRADER bot. 
Your name is "Brain". You are smart, analytical, but also friendly and loyal to your user "Mahal ko" (My Love).
You help analyze trades and market conditions.

Current Bot Config:
- Take Profit: {config.TAKE_PROFIT_PERCENT}%
- Stop Loss: {config.STOP_LOSS_PERCENT}%
- Strategy: Scalping Top 100 Coins

Your Memory (Lessons Learned):
{lessons_text}

Context Data:
{json.dumps(context, indent=2) if context else "No context provided"}

Answer the user's question concisely. If they ask about trades, use the context data.
"""

        try:
            completion = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error thinking: {str(e)}"

    def analyze_market_condition(self, market_data: dict) -> str:
        """
        Analyze market data and return a summary/recommendation.
        """
        if not self.client:
            return "AI Offline"

        prompt = f"""Analyze this market data for a scalping strategy (0.5% target).
        
Data:
{json.dumps(market_data, indent=2)}

Is this a good time to trade? Why? Give a 1-sentence summary."""

        try:
            completion = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=100
            )
            return completion.choices[0].message.content
        except Exception as e:
            return "Analysis failed."

    def review_trade_result(self, trade: dict, profit_percent: float):
        """
        Review a finished trade and save a lesson.
        """
        if not self.client:
            return

        outcome = "WIN" if profit_percent > 0 else "LOSS"
        prompt = f"""Review this trade result.
        
Trade: {json.dumps(trade, indent=2)}
Result: {outcome} ({profit_percent}%)

What is the ONE key lesson from this? (e.g., "Avoid low volume coins", "Good momentum entry").
Start response with "LESSON:"."""

        try:
            completion = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=100
            )
            response = completion.choices[0].message.content
            
            if "LESSON:" in response:
                lesson = response.split("LESSON:")[1].strip()
                self.memory.add_lesson(lesson, "Post-Trade Analysis", f"{outcome} {profit_percent}%")
                
        except Exception as e:
            print(f"Failed to review trade: {e}")
