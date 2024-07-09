from openai import OpenAI

# Initialize the AI client
client = OpenAI(
    base_url="https://api.novita.ai/v3/openai",
    api_key="1c089fd3-7ea2-4e14-a0ca-49f57b5be7f5",
)

model = "Nous-Hermes-2-Mixtral-8x7B-DPO"
max_tokens = 512


def generate_ai_explanation(console_output):
    prompt = f"""
    You are an artificial intelligence assistant for an impure simplified lambda calculus programming language.
    Your task is to explain the entire console output processing of lambda calculus expressions step by step, 
    and return the final result as a string.
    
    Console Output: {console_output}
    """
    try:
        completion_res = client.completions.create(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
            stream=False
        )
        ai_explanation = completion_res.choices[0].text.strip()
        return ai_explanation
    except Exception as e:
        print(f"Error generating AI explanation: {e}")
        return "Failed to generate AI explanation."
