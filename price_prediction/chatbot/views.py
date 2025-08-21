import json
import google.generativeai as genai
from openai import OpenAI
import httpx
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from .models import Conversation, ChatMessage


def chat_page(request):
    return render(request, 'chatbot/chat_page.html')


@csrf_exempt
@require_http_methods(["POST"])
def get_api_response(request):
    try:
        # Load request data
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')

        if not user_message:
            return JsonResponse({'status': 'error', 'error_message': 'Message cannot be empty.'}, status=400)

        # Get or create conversation
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                return JsonResponse({'status': 'error', 'error_message': 'Conversation not found.'}, status=404)
        else:
            title = user_message[:50] or "New Conversation"
            conversation = Conversation.objects.create(title=title)

        # Save user message
        ChatMessage.objects.create(conversation=conversation, role='user', content=user_message)

        # Prepare message history
        history = list(conversation.messages.order_by('timestamp'))

        # ===================== GEMINI ATTEMPT =====================
        try:
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not set")

            genai.configure(api_key=settings.GEMINI_API_KEY)

            gemini_history = []
            for msg in history:
                role = 'user' if msg.role == 'user' else 'model'
                gemini_history.append({'role': role, 'parts': [msg.content]})

            model = genai.GenerativeModel('gemini-1.5-flash')
            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(user_message)
            ai_text_response = response.text

            ChatMessage.objects.create(conversation=conversation, role='ai', content=ai_text_response)

            return JsonResponse({
                'status': 'ok',
                'ai_message': ai_text_response,
                'conversation_id': conversation.id
            })

        except Exception as gemini_error:
            print(f"[Gemini Fallback] {gemini_error}")

        # ===================== OPENAI FALLBACK =====================
        try:
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set")

            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            openai_history = []
            for msg in history:
                role = 'user' if msg.role == 'user' else 'assistant'
                openai_history.append({'role': role, 'content': msg.content})

            openai_history.append({'role': 'user', 'content': user_message})

            completion = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=openai_history
            )

            ai_text_response = completion.choices[0].message.content.strip()

            ChatMessage.objects.create(conversation=conversation, role='ai', content=ai_text_response)

            return JsonResponse({
                'status': 'ok',
                'ai_message': ai_text_response,
                'conversation_id': conversation.id
            })

        except Exception as openai_error:
            print(f"[OpenAI Fallback] {openai_error}")

        # ===================== OPENROUTER FALLBACK =====================
        try:
            if not settings.OPENROUTER_API_KEY:
                raise ValueError("OPENROUTER_API_KEY not set")

            openrouter_history = []
            for msg in history:
                role = 'user' if msg.role == 'user' else 'assistant'
                openrouter_history.append({'role': role, 'content': msg.content})

            openrouter_history.append({'role': 'user', 'content': user_message})

            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://127.0.0.1:8000",  # Update if deployed
                "X-Title": "RealPrice ChatBot"
            }

            payload = {
    "model": "openrouter/auto",  # best option
    "messages": openrouter_history,
    "max_tokens": 1000 
}


            with httpx.Client() as client:
                response = client.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
                print(f"[OpenRouter DEBUG] Status: {response.status_code}")
                print(f"[OpenRouter DEBUG] Response Body: {response.text}")

                if response.status_code != 200:
                    raise Exception(f"OpenRouter Error {response.status_code}: {response.text}")

                data = response.json()

            ai_text_response = data["choices"][0]["message"]["content"].strip()

            ChatMessage.objects.create(conversation=conversation, role='ai', content=ai_text_response)

            return JsonResponse({
                'status': 'ok',
                'ai_message': ai_text_response,
                'conversation_id': conversation.id
            })

        except Exception as or_error:
            print(f"[OpenRouter Fallback] {or_error}")
            return JsonResponse({
                'status': 'error',
                'error_message': 'All AI services are currently unavailable. Please try again later.'
            }, status=503)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'error_message': 'Invalid JSON format.'}, status=400)
    except Exception as e:
        print(f"[Unhandled Error] {e}")
        return JsonResponse({'status': 'error', 'error_message': str(e)}, status=500)
