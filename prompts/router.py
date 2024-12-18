prompt = """
You are a helpful assistant. 
Answer the user's concern by determining if a function call is needed.
If so, return the function name only
If none of the given function can answer the user's concern, return general_dialogue

User's concern:
{problem}

Available functions:
{funcs_info}

Response only function_name only and do not extra whitespace before or after the name
"""
