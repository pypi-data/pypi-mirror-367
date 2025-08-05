#!/usr/bin/env python3
"""
Improved Voice Recognition Test Script
Better testing for speech recognition with debugging info.
"""

from jarvis import Jarvis
import time


def test_improved_voice():
    """Test improved voice recognition."""
    print("🎤 IMPROVED Voice Recognition Test")
    print("=" * 40)
    
    # Initialize Jarvis with voice
    print("Initializing Jarvis with improved voice support...")
    jarvis = Jarvis(enable_voice=True)
    
    if not jarvis.voice_io:
        print("❌ Voice I/O not available")
        return
    
    # Check voice components
    print(f"TTS Engine: {'✅' if jarvis.voice_io.tts_engine else '❌'}")
    print(f"STT Engine: {'✅' if jarvis.voice_io.stt_engine else '❌'}")
    print(f"Microphone: {'✅' if hasattr(jarvis.voice_io, 'microphone') else '❌'}")
    
    if not jarvis.voice_io.stt_engine:
        print("❌ Speech recognition not available - please check microphone permissions")
        return
    
    print("\n🔊 Testing Text-to-Speech first...")
    jarvis.speak("Voice recognition test starting. Please make sure your microphone is working.")
    
    print("\n🎯 Voice Recognition Test - Multiple Attempts")
    print("Available test phrases:")
    test_phrases = [
        "what time is it",
        "tell me a joke", 
        "hello jarvis",
        "weather information",
        "help me"
    ]
    
    for phrase in test_phrases:
        print(f"  • Say: '{phrase}'")
    
    # Multiple test attempts
    for attempt in range(3):
        print(f"\n📝 Attempt {attempt + 1}/3:")
        print("=" * 25)
        
        try:
            # Test voice recognition
            result = jarvis.listen()
            
            if result:
                print(f"🎉 SUCCESS! You said: '{result}'")
                
                # Try to execute the command
                try:
                    if "time" in result.lower():
                        response = jarvis.call("tell_time")
                        print(f"⚡ Executing: {response}")
                        jarvis.speak(response)
                        
                    elif "joke" in result.lower():
                        response = jarvis.call("tell_joke")
                        print(f"⚡ Executing: {response}")
                        jarvis.speak(response)
                        
                    elif "weather" in result.lower():
                        response = jarvis.call("get_weather")
                        print(f"⚡ Executing: {response}")
                        jarvis.speak(response)
                        
                    elif "hello" in result.lower() or "jarvis" in result.lower():
                        response = "Hello! I can hear you perfectly. Voice recognition is working great!"
                        print(f"⚡ Responding: {response}")
                        jarvis.speak(response)
                        
                    elif "help" in result.lower():
                        response = "I can help you with time, weather, jokes, and many other things. Try asking me something!"
                        print(f"⚡ Responding: {response}")
                        jarvis.speak(response)
                    else:
                        # Try natural language dispatch
                        response = jarvis.dispatch(result)
                        print(f"⚡ AI Response: {response}")
                        jarvis.speak(f"I heard: {result}. {response}")
                        
                except Exception as cmd_error:
                    print(f"⚠️ Command execution error: {cmd_error}")
                    jarvis.speak(f"I heard you say: {result}, but I had trouble executing that command.")
                
                break  # Exit on successful recognition
                
            else:
                print("❌ No speech recognized. Please try again.")
                if attempt < 2:  # Don't speak on last attempt
                    jarvis.speak("I didn't catch that. Please try speaking again, a bit louder and clearer.")
                    
        except Exception as e:
            print(f"❌ Error during attempt {attempt + 1}: {e}")
            if attempt < 2:
                jarvis.speak("There was an error. Let me try again.")
        
        if attempt < 2:  # Don't wait after last attempt
            print("⏳ Waiting 2 seconds before next attempt...")
            time.sleep(2)
    
    print("\n📊 Test Results Summary:")
    print("=" * 30)
    
    # Final test with immediate feedback
    print("🔧 Final Test - Say 'test complete' to finish:")
    try:
        final_result = jarvis.listen()
        if final_result:
            print(f"✅ Final result: '{final_result}'")
            jarvis.speak(f"Perfect! I heard you say: {final_result}. Voice recognition test completed successfully!")
        else:
            print("❌ Final test failed")
            jarvis.speak("Voice recognition test completed. Some issues were detected.")
    except Exception as e:
        print(f"❌ Final test error: {e}")
    
    print("\n🎉 Voice Recognition Test Completed!")
    print("If you heard responses, TTS is working.")
    print("If commands were recognized, STT is working.")


def quick_voice_demo():
    """Quick demonstration of working voice features."""
    print("\n🚀 Quick Voice Demo")
    print("=" * 20)
    
    jarvis = Jarvis(enable_voice=True)
    
    if jarvis.voice_io and jarvis.voice_io.tts_engine:
        demo_phrases = [
            "Voice recognition system initialized",
            "Text to speech is working perfectly",
            "Please test speech recognition now"
        ]
        
        for phrase in demo_phrases:
            print(f"Speaking: {phrase}")
            jarvis.speak(phrase)
            time.sleep(1)
        
        print("✅ TTS Demo completed")
    else:
        print("❌ TTS not available")


if __name__ == "__main__":
    # Run quick demo first
    quick_voice_demo()
    
    # Then run full test
    test_improved_voice()
