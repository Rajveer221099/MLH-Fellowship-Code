using System;
using System.Speech.Recognition;
using System.Speech.Synthesis;

public class VoiceAssistant
{
    private SpeechRecognitionEngine recognizer;
    private SpeechSynthesizer synthesizer;

    public VoiceAssistant()
    {
        recognizer = new SpeechRecognitionEngine();
        synthesizer = new SpeechSynthesizer();

        recognizer.SetInputToDefaultAudioDevice();
        recognizer.SpeechRecognized += Recognizer_SpeechRecognized;
    }

    public void StartListening()
    {
        Console.WriteLine("Voice assistant is listening...");

        recognizer.RecognizeAsync(RecognizeMode.Multiple);
        Console.ReadLine();
    }

    private void Recognizer_SpeechRecognized(object sender, SpeechRecognizedEventArgs e)
    {
        string command = e.Result.Text;
        Console.WriteLine($"You said: {command}");

        // Add your logic to handle different commands and generate appropriate responses
        string response = GenerateResponse(command);
        
        // Speak the response
        synthesizer.Speak(response);
        
        Console.WriteLine($"Assistant: {response}");
    }

    private string GenerateResponse(string command)
    {
        // Add your own logic here to generate appropriate responses based on the command
        // You can use if-else statements, switch cases, or even implement more advanced natural language processing techniques

        // For example, let's assume the command "What's the time?" asks for the current time
        if (command.ToLower().Contains("time"))
        {
            DateTime currentTime = DateTime.Now;
            return $"The current time is {currentTime.ToString("HH:mm")}";
        }
        
        // If no specific command matches, provide a generic response
        return "I'm sorry, I cannot understand the command.";
    }
}

public class Program
{
    public static void Main()
    {
        VoiceAssistant assistant = new VoiceAssistant();
        assistant.StartListening();
    }
}
