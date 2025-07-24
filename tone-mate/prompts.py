def generate_prompt(tone, message):
    """
    Generate a context-aware prompt that produces appropriate responses
    based on the message content and requested tone.
    """
    
    message_lower = message.lower()
    is_resignation = any(word in message_lower for word in ['resign', 'leaving', 'quit', 'departure', 'last day', 'step down'])
    is_complaint = any(word in message_lower for word in ['complain', 'issue', 'problem', 'dissatisfied', 'unhappy'])
    is_request = any(word in message_lower for word in ['request', 'need', 'asking', 'could you', 'would you', 'please'])
    is_thank_you = any(word in message_lower for word in ['thank', 'grateful', 'appreciate', 'thanks'])
    
    tone_instructions = {
        "Professional": {
            "default": "Use formal business language, complete sentences, avoid contractions, maintain professional etiquette, be clear and direct.",
            "resignation": "Use formal resignation language, express gratitude for opportunities, maintain professionalism, provide clear timeline.",
            "complaint": "Use diplomatic language, focus on facts, suggest solutions, maintain professional courtesy.",
            "request": "Use polite formal language, clearly state the request, provide context, express appreciation."
        },
        "Friendly": {
            "default": "Use warm, conversational language, include appropriate contractions, be approachable and personable while maintaining respect.",
            "resignation": "Use warm but respectful language, express positive memories, maintain professionalism despite friendly tone.",
            "complaint": "Use gentle, understanding language while clearly stating concerns, focus on resolution.",
            "request": "Use warm, polite language, make the request conversational but clear."
        },
        "Apologetic": {
            "default": "Express genuine regret appropriately, acknowledge any inconvenience, use empathetic language, offer solutions.",
            "resignation": "Apologize for any inconvenience caused by departure, express regret about leaving team, offer smooth transition.",
            "complaint": "Acknowledge the situation with regret, express understanding, focus on resolution.",
            "request": "Apologize for any inconvenience the request may cause, express appreciation for consideration."
        },
        "Assertive": {
            "default": "Be direct and confident, state needs clearly, maintain respect while being firm, focus on outcomes.",
            "resignation": "Clearly state decision to leave, be firm about timeline, maintain respect but don't over-explain.",
            "complaint": "Clearly state the issue, be direct about needed resolution, maintain professional firmness.",
            "request": "State request clearly and confidently, provide clear reasoning, expect positive response."
        },
        "Casual": {
            "default": "Use relaxed, informal language with contractions, be conversational and laid-back while remaining appropriate.",
            "resignation": "Use informal but respectful language, keep it straightforward, maintain some level of professionalism.",
            "complaint": "Use casual but clear language to express concerns, focus on simple resolution.",
            "request": "Use informal, friendly language to make the request, keep it simple and direct."
        },
        "Empathetic": {
            "default": "Show understanding of others' perspectives, acknowledge feelings, use supportive and compassionate language.",
            "resignation": "Show understanding of impact on team, express care for colleagues, offer support during transition.",
            "complaint": "Acknowledge the difficulty of the situation, show understanding, focus on mutual resolution.",
            "request": "Show understanding of recipient's position, acknowledge any burden the request may cause."
        },
        "Encouraging": {
            "default": "Use positive, uplifting language, express confidence in others, motivate positive outcomes.",
            "resignation": "Express confidence in team's future success, encourage continued excellence, maintain positive outlook.",
            "complaint": "Focus on positive resolution, encourage improvement, express confidence in solution.",
            "request": "Express confidence in positive response, encourage collaboration, use optimistic language."
        },
        "Formal": {
            "default": "Use traditional business language, avoid contractions, maintain proper structure and strict etiquette.",
            "resignation": "Use highly formal resignation protocol, include proper notices, maintain ceremonial respect.",
            "complaint": "Use formal complaint structure, focus on policy and procedure, maintain official tone.",
            "request": "Use formal request structure, include proper justification, maintain official protocol."
        },
        "Witty": {
            "default": "Include light, appropriate humor, be clever with word choice, maintain professionalism while being engaging.",
            "resignation": "Use subtle, respectful humor, keep wit appropriate for farewell context, maintain professionalism.",
            "complaint": "Use very light humor to soften complaint, focus on clever problem-solving, maintain respect.",
            "request": "Use light humor to make request more engaging, keep wit appropriate and professional."
        },
        "Motivational": {
            "default": "Use inspiring language appropriately, focus on positive outcomes and growth opportunities.",
            "resignation": "Frame departure as positive growth opportunity, inspire team's continued success, maintain professional optimism.",
            "complaint": "Focus on opportunity for improvement, inspire positive change, maintain constructive outlook.",
            "request": "Frame request as opportunity for collaboration, inspire positive action, focus on mutual benefits."
        },
        "Sympathetic": {
            "default": "Show care and concern appropriately, acknowledge difficulties, use gentle and understanding language.",
            "resignation": "Express understanding of impact, show concern for team transition, offer gentle support.",
            "complaint": "Show concern for the issues raised, express sympathy for difficulties, focus on caring resolution.",
            "request": "Show understanding of any inconvenience, express sympathy for additional workload."
        },
        "Grateful": {
            "default": "Express appreciation clearly and genuinely, acknowledge efforts or help received, be warm and thankful.",
            "resignation": "Express deep gratitude for opportunities and experiences, thank colleagues and leadership warmly.",
            "complaint": "Thank recipient for their time and attention, express appreciation for their efforts to resolve.",
            "request": "Express gratitude for consideration, thank recipient in advance, show appreciation for their help."
        },
        "Persuasive": {
            "default": "Use compelling but respectful language, present clear benefits, guide toward desired outcome diplomatically.",
            "resignation": "Present resignation as thoughtful decision, emphasize positive aspects of departure, maintain professional persuasion.",
            "complaint": "Present issues convincingly, focus on benefits of resolution, persuade toward positive action.",
            "request": "Present compelling reasons for request, highlight mutual benefits, persuade respectfully."
        },
        "Respectful": {
            "default": "Maintain high courtesy and politeness, use appropriate titles, show deep consideration for the recipient.",
            "resignation": "Show maximum respect for leadership and colleagues, honor company and relationships, maintain dignity.",
            "complaint": "Express concerns with utmost respect, honor recipient's position, maintain courteous approach.",
            "request": "Make request with deep respect, honor recipient's time and position, maintain high courtesy."
        },
        "Neutral": {
            "default": "Use balanced, objective language, avoid emotional words, be clear and straightforward without bias.",
            "resignation": "State resignation factually, provide necessary information, avoid emotional language, be direct.",
            "complaint": "Present issues objectively, focus on facts, avoid emotional language, seek practical resolution.",
            "request": "State request clearly and factually, provide objective reasoning, avoid emotional appeal."
        }
    }
    strength_modifiers = {
    1: "Apply the tone subtly and gently",
    2: "Apply the tone lightly", 
    3: "Apply the tone moderately",
    4: "Apply the tone strongly",
    5: "Apply the tone very prominently"
}
    context = "default"
    if is_resignation:
        context = "resignation"
    elif is_complaint:
        context = "complaint"
    elif is_request:
        context = "request"
    
    tone_data = tone_instructions.get(tone, tone_instructions["Neutral"])
    specific_instruction = tone_data.get(context, tone_data["default"])
    
    return f"""Rewrite the following message in a {tone.lower()} tone, considering the context and purpose of the message. {specific_instruction}

IMPORTANT: 
- Provide ONLY the rewritten message
- Do not include explanations, introductions, or commentary
- Keep the core message and intent intact
- Ensure the tone is appropriate for the context
- Maintain professional standards regardless of tone choice

Message to rewrite:
{message}"""