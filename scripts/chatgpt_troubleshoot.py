#!/usr/bin/env python3
"""
ChatGPT Troubleshooting Script - Versão Mínima
Script para análise automática de erros em pipelines CI/CD usando OpenAI GPT-4
"""

import os
import sys
import json
import requests
from datetime import datetime
import re


def summarize(text: str, max_chars: int = 4000) -> str:
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_chars:
        return text
    head = text[: max_chars // 2]
    tail = text[-(max_chars // 2) :]
    return head + "\n...\n" + tail


def main():
    """Main function to run troubleshooting analysis."""

    # Capturar variáveis de ambiente
    api_key = os.environ.get('OPENAI_API_KEY')
    error_type = os.environ.get('ERROR_TYPE', 'unknown_error')
    error_message = os.environ.get('ERROR_MESSAGE', '').strip()
    workflow_name = os.environ.get('WORKFLOW_NAME', 'Unknown Workflow')
    repository = os.environ.get('REPOSITORY', 'Unknown Repository')
    branch = os.environ.get('BRANCH', 'Unknown Branch')
    commit = os.environ.get('COMMIT', 'Unknown Commit')

    print("🤖 INICIANDO ANÁLISE DE TROUBLESHOOTING COM CHATGPT")
    print("=" * 60)
    print(f"Workflow: {workflow_name}")
    print(f"Repository: {repository}")
    print(f"Branch: {branch}")
    print(f"Error Type: {error_type}")
    if error_message:
        print("Erro específico detectado (trecho):")
        print(summarize(error_message, 800))
    print("=" * 60)

    if not api_key:
        print("❌ ERRO: OPENAI_API_KEY não configurado")
        print("\nPara configurar:")
        print("1. Acesse https://platform.openai.com/api-keys")
        print("2. Crie uma nova API key")
        print("3. Configure como secret no GitHub: Settings > Secrets > OPENAI_API_KEY")
        sys.exit(1)

    # Heurística rápida para região inválida do Azure
    azure_region_hint = ""
    if re.search(r"was not found in the list of supported Azure Locations", error_message, re.IGNORECASE):
        azure_region_hint = (
            "Parece ser uma região inválida do Azure. Corrija a variável 'location' no Terraform para uma região válida (ex.: eastus, eastus2, uksouth)."
        )

    # Construir prompt para ChatGPT
    prompt = f"""
    Você é um especialista em DevOps e troubleshooting de pipelines CI/CD.

    CONTEXTO DO ERRO:
    - Pipeline: {workflow_name}
    - Repositório: {repository}
    - Branch: {branch}
    - Commit: {commit}
    - Tipo de Erro: {error_type}
    - Timestamp: {datetime.now().isoformat()}

    MENSAGEM DE ERRO ESPECÍFICA (trecho):
    {summarize(error_message, 2000) if error_message else 'N/A'}

    DETALHES DO PROBLEMA:
    A pipeline falhou durante a execução. Baseado no tipo de erro e NA MENSAGEM ESPECÍFICA acima, forneça:

    ## 🔍 DIAGNÓSTICO
    Explique exatamente o que causou o erro, citando a linha/trecho relevante da mensagem quando útil.

    ## 🛠️ SOLUÇÕES IMEDIATAS
    Liste 3-5 ações concretas e específicas para este caso.

    ## 🚀 IMPLEMENTAÇÃO
    Inclua comandos/snippets aplicáveis ao contexto.

    ## 🛡️ PREVENÇÃO
    Sugira como evitar este erro no futuro.

    {('DICA ADICIONAL: ' + azure_region_hint) if azure_region_hint else ''}

    Seja objetivo e específico para ESTE erro.
    """

    # Fazer chamada para OpenAI API
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        'model': 'gpt-4o-mini',
        'messages': [
            {
                'role': 'system',
                'content': 'Você é um especialista em DevOps e troubleshooting de pipelines CI/CD. Responda de forma prática e específica ao erro informado.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'max_tokens': 1200,
        'temperature': 0.2
    }

    try:
        print("🔍 Analisando erro com ChatGPT...")
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=45
        )
        response.raise_for_status()

        result = response.json()
        troubleshooting_advice = result['choices'][0]['message']['content']

        print("✅ ANÁLISE CONCLUÍDA COM SUCESSO")
        print("\n" + "="*60)
        print(troubleshooting_advice)
        print("="*60)

        # Salvar resultado em arquivo
        with open('troubleshooting_report.md', 'w', encoding='utf-8') as f:
            f.write(f"# 🤖 Troubleshooting Report\n\n")
            f.write(f"**Pipeline:** {workflow_name}\n")
            f.write(f"**Repository:** {repository}\n")
            f.write(f"**Branch:** {branch}\n")
            f.write(f"**Commit:** {commit}\n")
            f.write(f"**Error Type:** {error_type}\n")
            if error_message:
                f.write(f"**Error Message (excerpt):**\n\n{summarize(error_message, 1500)}\n\n")
            f.write(f"**Timestamp:** {datetime.now().isoformat()}\n\n")
            f.write("## ChatGPT Analysis\n\n")
            f.write(troubleshooting_advice)

        print(f"\n📄 Relatório salvo em: troubleshooting_report.md")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar com OpenAI API: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
