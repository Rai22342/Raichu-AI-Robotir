import customtkinter as ctk
import threading
import time
import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import google.generativeai as genai

# --- কনফিগারেশন ---
# এখানে আপনার Gemini API Key দিন
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel('gemini-pro')

class RaichuRobot:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Raichu - AI Robot")
        self.root.geometry("450x650")
        ctk.set_appearance_mode("dark")
        
        pygame.mixer.init()

        # UI ডিজাইন (HTML ফাইলের থিম অনুযায়ী)
        self.label = ctk.CTkLabel(self.root, text="⚡ RAICHU", font=("Orbitron", 28, "bold"), text_color="#00dcff")
        self.label.pack(pady=20)

        self.status_label = ctk.CTkLabel(self.root, text="SYSTEM ONLINE", font=("Orbitron", 12), text_color="#00ff88")
        self.status_label.pack(pady=5)

        self.chat_display = ctk.CTkTextbox(self.root, width=400, height=350, corner_radius=15, border_width=1, border_color="#3a5a68")
        self.chat_display.pack(pady=20)

        self.mic_button = ctk.CTkButton(self.root, text="🎤 কথা বলুন", command=self.start_voice_thread, 
                                       fg_color="#6c3fff", hover_color="#00dcff", font=("Noto Sans Bengali", 14), height=45)
        self.mic_button.pack(pady=10)

        # প্রতি ১২ সেকেন্ড পর পর 'I am Raichu' বলার জন্য থ্রেড
        threading.Thread(target=self.announcement_loop, daemon=True).start()

    def speak(self, text, slow=False):
        """টেক্সটকে ভয়েসে রূপান্তর করে প্লে করে"""
        try:
            tts = gTTS(text=text, lang='bn', slow=slow)
            tts.save("speech.mp3")
            pygame.mixer.music.load("speech.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.music.unload()
            os.remove("speech.mp3")
        except Exception as e:
            print(f"Error: {e}")

    def get_ai_response(self, prompt):
        """Gemini থেকে এলিয়েন স্টাইলে উত্তর আনা"""
        # এলিয়েন স্টাইল নিশ্চিত করার জন্য সিস্টেম প্রম্পট
        alien_context = (
            "তুমি একজন অদ্ভুত এলিয়েন রোবট যার নাম Raichu। "
            "তোমার কথা বলার ভঙ্গি হবে রহস্যময়, যান্ত্রিক এবং এলিয়েনদের মতো। "
            "সবসময় বাংলায় উত্তর দাও কিন্তু মাঝে মাঝে অদ্ভুত শব্দ ব্যবহার করো। "
            "প্রশ্ন: "
        )
        try:
            response = model.generate_content(alien_context + prompt)
            return response.text
        except:
            return "গ্যালাকটিক সিগন্যালে সমস্যা... আমি সংযোগ করতে পারছি না।"

    def listen(self):
        """ভয়েস ইনপুট নেওয়া"""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.status_label.configure(text="LISTENING...", text_color="#ff3c8a")
            try:
                audio = r.listen(source, timeout=5)
                text = r.recognize_google(audio, language="bn-BD")
                return text
            except:
                return None

    def process_interaction(self):
        user_text = self.listen()
        if user_text:
            self.chat_display.insert("end", f"আপনি: {user_text}\n\n")
            self.status_label.configure(text="THINKING...", text_color="#9b6fff")
            
            ai_reply = self.get_ai_response(user_text)
            self.chat_display.insert("end", f"Raichu: {ai_reply}\n\n")
            self.chat_display.see("end")
            
            self.status_label.configure(text="SPEAKING...", text_color="#00cc66")
            self.speak(ai_reply)
        
        self.status_label.configure(text="READY", text_color="#00dcff")

    def start_voice_thread(self):
        threading.Thread(target=self.process_interaction).start()

    def announcement_loop(self):
        """প্রতি ১২ সেকেন্ড অন্তর নাম ঘোষণা"""
        while True:
            time.sleep(12)
            # যদি বর্তমানে কোনো কথা না চলে তবেই বলবে
            if not pygame.mixer.music.get_busy():
                self.speak("আই এম রাইচু", slow=True)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = RaichuRobot()
    app.run()