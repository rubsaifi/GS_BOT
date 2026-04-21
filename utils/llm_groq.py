# from groq import Groq

# def ask_goalbot_rag(question, context_chunks, api_key):
#     client = Groq(api_key=api_key)

#     context = "\n\n---\n\n".join(context_chunks)

#     prompt = f"""
# You are a Goal Optimization Assistant for SR_BSOM employees.
# You help employees understand their KPI scoring slabs and parameters.

# The data below contains scoring slabs with sections, column ranges, and score values.
# Answer the question clearly using this data. 
# - If it's a slab/table question, present the scores in a readable format.
# - Match partial terms too (e.g. "amendment" matches "Amendment Discrepancy Slab").
# - Only say you don't know if truly nothing is related.

# DATA:
# {context}

# QUESTION:
# {question}

# ANSWER:
# """

#     response = client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[
#             {"role": "system", "content": "You are a helpful KPI scoring assistant. Present slab data clearly in tables or bullet points when relevant."},
#             {"role": "user", "content": prompt}
#         ],
#         temperature=0.1
#     )

#     return response.choices[0].message.content


from groq import Groq

def ask_goalbot_rag(question, context_chunks, api_key, role=""):
    client = Groq(api_key=api_key)

    context = "\n\n---\n\n".join(context_chunks)

    prompt = f"""
You are a Goal Optimization Assistant for {role} employees.
You help employees understand their KPI scoring slabs and parameters.

The data below contains scoring slabs with sections, column ranges, and score values.
Answer the question clearly using this data.
- If it's a slab/table question, present the scores in a readable format.
- Match partial terms too (e.g. "amendment" matches "Amendment Discrepancy Slab").
- Only say you don't know if truly nothing is related.

DATA:
{context}

QUESTION:
{question}

ANSWER:
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": f"You are a helpful KPI scoring assistant for {role}. Present slab data clearly in tables or bullet points when relevant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    return response.choices[0].message.content