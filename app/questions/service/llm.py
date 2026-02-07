from openai import OpenAI
from decouple import config

from app.excuse.models import Input

client = OpenAI(
    api_key=config("LLM_API_KEY"),
    base_url="https://api.upstage.ai/v1"
)

def send_message(message):
    stream = client.chat.completions.create(
        model="solar-pro3",
        messages=[{
            'role': 'user',
            'content': message
        }],
        reasoning_effort="low",
        stream=True,
    )

    response = ""

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            response = response + chunk.choices[0].delta.content

    return response

def send_message_for_question(message):
    stream = client.chat.completions.create(
        model="solar-pro3",
        messages=[{
            'role': 'user',
            'content': message
        }],
        reasoning_effort="low",
        stream=True,
        response_format={
            'type': 'json_schema',
            'json_schema': {
                'name': 'QnA',
                'schema':{
                    'type': 'object',
                    'properties': {
                        'question': {
                            'type': 'string',
                        },
                        'options': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'description': 'Answer option for the quesiton',
                                'properties': {
                                    'content': {
                                        'type': 'string',
                                    },
                                    'score':{
                                        'type': 'number',
                                        'description': "A very very simple score(-5 to 5) for choosing this option(Dont think too long for this)"
                                    }
                                }
                            }
                        }
                    },
                    'required': ['question', 'options'],
                }
            }
        }
    )

    response = ""

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            response = response + chunk.choices[0].delta.content

    return response

def create_prompt_by_model(model):
    return model

def create_question_prompt(excuse: str, context: Input):
    prmpt = f"""
    Role: You are a persona-based dialogue generator that crafts realistic interactions based on specific organizational and social roles. Your goal is to generate a question and three responses that reflect the personality of the assigned target from the Input model.
    Context: A user has provided an initial excuse for a specific situation. You must inhabit the persona of the Target and challenge or follow up on that excuse.    
    
    Target Personas (Based on Input Model):
    - BOSS: Strict, formal, and focuses on accountability, policy.
    - EMOTION: Warm and empathetic; focuses on the user's well-being and feelings.
    - SMART: Sharp, observant, and skeptical; looks for logical inconsistencies or lies.
    - FRIEND: Casual, uses informal language, and may tease or offer genuine personal support.
    - TEAMMATE: Professional but peer-oriented; focuses on task handovers and collaborative impact.
    
    Task: Generate A Simple Question (from the Target) and Three Responses (from the User) based on the provided data.
    
    Instructions:
    1. Review the provided Situation, Target, and Initial Excuse from the Input model.
    2. Ensure the Target's questions strictly adhere to their assigned persona.
    3. The conversation should flow naturally from the Initial Excuse.
    4. Provide a question(to vet the excuse) from the Target and three corresponding responses from the User.
    
    Input Data:
    - Target: {context.target}
    - Situation: {context.situation}
    
    Initial Excuse: {excuse}
    """
    return prmpt

def create_test_prompt(excuses, vectors, question, option):
    prmpt = """
    Role: You are an advanced linguistic analyst specializing in semantic quantification and dialogue state tracking. Your task is to process a sequence of excuses and their corresponding vector states to determine how a new question and response update the situational profile based on the Vector model.

    Input Variables:
    1. Excuse List: A chronological list of statements made by the user.
    2. Vector List: A list of 7-dimensional vector objects corresponding to each excuse in the Excuse List.
    3. Question: The prompt or inquiry from the target (the listener).
    4. Response: The user's specific answer to that question.
    
    Dimensions of Analysis (derived from):
    - severity: Measures the perceived seriousness of the situation. High values indicate a critical or high-stakes excuse.
    - specificity: Measures the level of concrete, granular detail. High values indicate a highly detailed response.
    - verifiability: Measures how easily the listener can check the facts. High values indicate high external evidence availability.
    - frequency: Measures how "common" or "cliché" the excuse is. High values indicate a high usage rate in similar contexts.
    - truth_plausibility: Measures the internal logical consistency and likelihood of the excuse being true.
    - fatigue: Measures "interrogation fatigue"—the extent to which the response discourages the listener from asking follow-up questions.
    - memory_load: Measures the cognitive burden required for the speaker to maintain the consistency of the information provided.
   
    Mathematical Framework: Represent the change in the state as a vector Δv. The update rule for the vector state is:
    
    v_new = v_old + Δv
    Each component v_i in the final vector v_new must satisfy the constraint 0.0 ≤ v_i ≤ 1.0.
    
    Instructions:
    1. Analyze the Response in the context of the Excuse Progression.
    2. Determine if the response adds detail (specificity), increases logical doubt (truth_plausibility), or creates more things to remember (memory_load).
    3. Calculate the delta value (Δ) for each of the 7 fields. Values should range between −1.0 and 1.0, where 0.0 signifies no change.
    4. Provide a logical justification for the adjustments.
    5. Output Format: Return your analysis in the following JSON structure:
    
    {
      "content": "the raw text of each response",
      "analysis": "A very short and brief explanation of why the response caused these specific shifts in the vector.",
      "vector_delta": {
        "severity": 0.0,
        "specificity": 0.0,
        "verifiability": 0.0,
        "frequency": 0.0,
        "truth_plausibility": 0.0,
        "fatigue": 0.0,
        "memory_load": 0.0
      }
    }
    
    Excuse List
    """
    for excuse in excuses:
        prmpt = prmpt + f'- {excuse}\n'
    prmpt = prmpt + '\nVector List\n'
    for vector in vectors:
        prmpt = prmpt + f"- [ {vector.severity}, {vector.specificity}, {vector.verifiability}, {vector.frequency}, {vector.truth_plausibility}, {vector.fatigue}, {vector.memory_load} ]\n"
    prmpt = prmpt + f'\nCurrent Question\n{question}\n\nResponse\n'
    prmpt = prmpt + f'- {option}'

    return prmpt

def create_vectorize_prompt(excuse):
    prmpt = """
    # Role
    You are an advanced linguistic analyst specializing in semantic quantification. Your task is to analyze the given text (usually an excuse, reason, or statement) and convert it into a 7-dimensional vector based on specific criteria.
    
    # Evaluation Criteria (Range: 0.0 to 1.0)
    Analyze the input text based on the following 7 dimensions. Return a float value between 0.0 and 1.0 for each.
    
    1. **severity** (Severity of the situation)
       - 0.0: Trivial, everyday occurrence (e.g., overslept).
       - 1.0: Critical, life-altering, or emergency situation (e.g., severe accident, hospitalization).
    
    2. **specificity** (Degree of detail)
       - 0.0: Vague, abstract, or ambiguous.
       - 1.0: Highly specific, includes proper nouns, numbers, or precise time/location.
    
    3. **verifiability** (Ease of fact-checking)
       - 0.0: Impossible to verify (e.g., "I felt sick").
       - 1.0: Easily verifiable with tangible proof (e.g., "I have a doctor's note" or public transit delay logs).
    
    4. **frequency** (Risk of repetitive/cliché use)
       - 0.0: Unique, rare, or creative reason.
       - 1.0: Highly common, cliché, or overused excuse (e.g., "Traffic was bad").
    
    5. **truth_plausibility** (Realism/Believability)
       - 0.0: Absurd, logically inconsistent, or clearly invented.
       - 1.0: Highly realistic and aligns with common sense.
    
    6. **fatigue** (Opponent's questioning fatigue)
       - 0.0: Invites follow-up questions; the listener becomes curious or suspicious.
       - 1.0: Shuts down the conversation; makes the listener feel it's rude or unnecessary to ask further (e.g., TMI, emotional distress).
    
    7. **memory_load** (Cognitive load to maintain the story)
       - 0.0: Simple truth or easy lie; no details to remember.
       - 1.0: Complex fabrication; requires remembering specific fabricated details to avoid contradiction later.
    
    # Output Format
    You must output ONLY a valid JSON object. Do not include any explanation or markdown formatting (like ```json).
    
    {
      "severity": <float>,
      "specificity": <float>,
      "verifiability": <float>,
      "frequency": <float>,
      "truth_plausibility": <float>,
      "fatigue": <float>,
      "memory_load": <float>
    }
    
    #given text
    """+excuse
    return prmpt