import openai

# Initialize the AI client
client = openai.OpenAI(
    api_key="1c089fd3-7ea2-4e14-a0ca-49f57b5be7f5",
)

model = "Nous-Hermes-2-Mixtral-8x7B-DPO"
max_tokens = 512


async def generate_ai_explanation(console_output):
    prompt = f"""
    You are an artificial intelligence assistant for an impure simplified lambda calculus programming language 
    called 'JAKK'.
    For every input given, explain in detail a step-by-step breakdown for each action done in the final output 
    and console and output sections of the code from that input expression. 
    If they are errors, explain them also. 

    Console Output:
    {console_output}

    ASSISTANT:
    """
    try:
        completion_res = await client.completions.create(
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
