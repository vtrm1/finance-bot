# WhatsApp Finance Bot

Bot para WhatsApp que registra e organiza gastos usando Twilio e OpenAI.

## Variáveis de ambiente necessárias

- `TWILIO_ACCOUNT_SID` - SID da conta Twilio
- `TWILIO_AUTH_TOKEN` - Token de autenticação Twilio
- `OPENAI_API_KEY` - Chave da API OpenAI

## Deploy no Railway

1. Crie um repositório no GitHub e envie este projeto.
2. Crie uma conta no https://railway.app e conecte seu repositório.
3. Configure as variáveis de ambiente no painel do Railway.
4. Faça deploy e obtenha a URL pública.
5. Configure o webhook no Twilio para apontar para `https://<seu-app>.railway.app/webhook`.

## Uso

Envie mensagens de texto ou áudio pelo WhatsApp para o número do Twilio Sandbox. O bot responderá com a organização dos gastos.
