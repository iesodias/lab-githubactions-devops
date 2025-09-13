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
import glob


def main():
    """Main function to run troubleshooting analysis."""
    
    # Capturar variáveis de ambiente
    api_key = os.environ.get('OPENAI_API_KEY')
    error_type = os.environ.get('ERROR_TYPE', 'unknown_error')
    error_logs = os.environ.get('ERROR_LOGS', '')
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
    print(f"Error Logs Available: {'Yes' if error_logs else 'No'}")
    print("=" * 60)
    
    if not api_key:
        print("❌ ERRO: OPENAI_API_KEY não configurado")
        print("\nPara configurar:")
        print("1. Acesse https://platform.openai.com/api-keys")
        print("2. Crie uma nova API key")
        print("3. Configure como secret no GitHub: Settings > Secrets > OPENAI_API_KEY")
        sys.exit(1)
    
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
    
    LOGS DE ERRO COMPLETOS:
    {error_logs}
    
    DETALHES DO PROBLEMA:
    A pipeline falhou durante a execução. Baseado nos LOGS DE ERRO ESPECÍFICOS acima, forneça uma análise detalhada:
    
    ## 🔍 DIAGNÓSTICO
    Analise EXATAMENTE as mensagens de erro dos logs acima e explique:
    - Qual é a causa raiz do problema
    - Em que linha/comando específico o erro ocorreu
    - Por que este erro aconteceu
    
    ## 🛠️ SOLUÇÕES IMEDIATAS
    Baseado nos logs de erro específicos, forneça 3-5 soluções práticas:
    - Comandos exatos para corrigir o problema
    - Arquivos que precisam ser modificados
    - Variáveis de ambiente que podem estar faltando
    
    ## 🚀 IMPLEMENTAÇÃO STEP-BY-STEP
    Forneça comandos específicos e sequenciais para resolver:
    ```bash
    # Exemplo de comandos específicos baseados no erro
    ```
    
    ## 🛡️ PREVENÇÃO FUTURA
    Como evitar que este erro específico aconteça novamente:
    - Verificações pré-commit
    - Testes locais
    - Configurações de ambiente
    
    ## 📋 CHECKLIST DE VERIFICAÇÃO
    - [ ] Verificar se [item específico do erro] está correto
    - [ ] Testar [comando específico] localmente
    - [ ] Confirmar [configuração específica]
    
    IMPORTANTE: Baseie sua resposta EXCLUSIVAMENTE nos logs de erro fornecidos. Seja específico e prático.
    """
    
    # Fazer chamada para OpenAI API
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'gpt-4',
        'messages': [
            {
                'role': 'system',
                'content': 'Você é um especialista em DevOps e troubleshooting de pipelines CI/CD. Forneça respostas técnicas, práticas e específicas.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'max_tokens': 1500,
        'temperature': 0.3
    }
    
    try:
        print("🔍 Analisando erro com ChatGPT...")
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        troubleshooting_advice = result['choices'][0]['message']['content']
        
        print(" ANÁLISE CONCLUÍDA COM SUCESSO")
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
            f.write(f"**Timestamp:** {datetime.now().isoformat()}\n\n")
            
            # Incluir logs de erro no relatório
            if error_logs:
                f.write("## Error Logs\n\n")
                f.write("```\n")
                f.write(error_logs)
                f.write("```\n\n")
            
            f.write("## ChatGPT Analysis\n\n")
            f.write(troubleshooting_advice)
        
        print(f"\n📄 Relatório salvo em: troubleshooting_report.md")
        
    except requests.exceptions.RequestException as e:
        print(f" Erro ao conectar com OpenAI API: {e}")
        sys.exit(1)
    except Exception as e:
        print(f" Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
