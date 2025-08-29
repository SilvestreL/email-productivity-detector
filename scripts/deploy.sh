#!/bin/bash

# 🚀 Deploy Automatizado - Email Productivity Classifier
# AutoU - One-Command Deploy

set -e  # Para em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para imprimir com cores
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header() {
    echo -e "${PURPLE}🚀 $1${NC}"
}

print_step() {
    echo -e "${CYAN}📋 $1${NC}"
}

# Configurações
PROJECT_NAME="email-productivity-classifier"
VERSION="1.0.0"
DOCKER_IMAGE="email-productivity-classifier"

# Verificar se o Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker não está instalado. Por favor, instale o Docker primeiro."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
        exit 1
    fi
    
    print_status "Docker e Docker Compose verificados"
}

# Verificar se o Git está instalado
check_git() {
    if ! command -v git &> /dev/null; then
        print_warning "Git não está instalado. Algumas funcionalidades podem não funcionar."
    else
        print_status "Git verificado"
    fi
}

# Build da imagem Docker
build_docker_image() {
    print_step "Construindo imagem Docker..."
    
    if docker build -t $DOCKER_IMAGE:$VERSION .; then
        print_status "Imagem Docker construída com sucesso"
        docker tag $DOCKER_IMAGE:$VERSION $DOCKER_IMAGE:latest
    else
        print_error "Falha ao construir imagem Docker"
        exit 1
    fi
}

# Deploy local
deploy_local() {
    print_header "Deploy Local"
    
    print_step "Parando containers existentes..."
    docker-compose down 2>/dev/null || true
    
    print_step "Iniciando aplicação..."
    if docker-compose up -d; then
        print_status "Aplicação iniciada com sucesso!"
        echo ""
        print_info "🌐 URLs de acesso:"
        echo "   📄 Interface HTML: http://localhost"
        echo "   🤖 App Streamlit: http://localhost:8501"
        echo "   🔗 API REST: http://localhost:8000"
        echo "   📚 Docs API: http://localhost:8000/docs"
        echo ""
        print_info "📊 Status dos containers:"
        docker-compose ps
    else
        print_error "Falha ao iniciar aplicação"
        exit 1
    fi
}

# Deploy com API
deploy_with_api() {
    print_header "Deploy com API REST"
    
    print_step "Parando containers existentes..."
    docker-compose down 2>/dev/null || true
    docker-compose -f docker-compose.api.yml down 2>/dev/null || true
    
    print_step "Iniciando aplicação com API..."
    if docker-compose -f docker-compose.api.yml up -d; then
        print_status "Aplicação com API iniciada com sucesso!"
        echo ""
        print_info "🌐 URLs de acesso:"
        echo "   📄 Interface HTML: http://localhost"
        echo "   🔗 API REST: http://localhost:8000"
        echo "   📚 Docs API: http://localhost:8000/docs"
        echo "   🌐 Via Nginx: http://localhost/api/"
        echo ""
        print_info "📊 Status dos containers:"
        docker-compose -f docker-compose.api.yml ps
    else
        print_error "Falha ao iniciar aplicação com API"
        exit 1
    fi
}

# Deploy para produção (simulado)
deploy_production() {
    print_header "Deploy para Produção (Simulado)"
    
    print_step "Verificando configurações de produção..."
    
    # Simular verificações de produção
    if [ -z "$PRODUCTION_ENV" ]; then
        print_warning "Variável PRODUCTION_ENV não definida. Usando configurações padrão."
    fi
    
    print_step "Construindo imagem otimizada para produção..."
    docker build -t $DOCKER_IMAGE:prod --target production . 2>/dev/null || \
    docker build -t $DOCKER_IMAGE:prod .
    
    print_step "Executando testes de produção..."
    python tests/test_model.py > /dev/null 2>&1 || print_warning "Alguns testes falharam"
    
    print_status "Deploy para produção simulado com sucesso!"
    echo ""
    print_info "📋 Próximos passos para produção real:"
    echo "   1. Configure variáveis de ambiente"
    echo "   2. Configure SSL/TLS"
    echo "   3. Configure monitoramento"
    echo "   4. Configure backup"
    echo "   5. Deploy em cloud (AWS, GCP, Azure)"
}

# Deploy para cloud (simulado)
deploy_cloud() {
    print_header "Deploy para Cloud (Simulado)"
    
    print_step "Verificando configurações de cloud..."
    
    # Simular deploy para diferentes clouds
    case $1 in
        "aws")
            print_step "Deploy para AWS ECS..."
            print_info "Comando simulado: aws ecs create-service --cluster email-classifier --service-name email-classifier-service"
            ;;
        "gcp")
            print_step "Deploy para Google Cloud Run..."
            print_info "Comando simulado: gcloud run deploy email-classifier --image gcr.io/project/email-classifier"
            ;;
        "azure")
            print_step "Deploy para Azure Container Instances..."
            print_info "Comando simulado: az container create --resource-group rg-email-classifier --name email-classifier"
            ;;
        *)
            print_step "Deploy para múltiplas clouds..."
            print_info "AWS ECS, Google Cloud Run, Azure Container Instances"
            ;;
    esac
    
    print_status "Deploy para cloud simulado com sucesso!"
    echo ""
    print_info "📋 Para deploy real em cloud:"
    echo "   1. Configure credenciais da cloud"
    echo "   2. Configure registry de imagens"
    echo "   3. Configure networking e segurança"
    echo "   4. Configure monitoramento e logs"
}

# Health check
health_check() {
    print_step "Verificando saúde da aplicação..."
    
    # Aguardar um pouco para a aplicação inicializar
    sleep 5
    
    # Testar endpoints
    if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        print_status "Streamlit: OK"
    else
        print_warning "Streamlit: Não respondeu"
    fi
    
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_status "API REST: OK"
    else
        print_warning "API REST: Não respondeu"
    fi
    
    if curl -f http://localhost > /dev/null 2>&1; then
        print_status "Nginx: OK"
    else
        print_warning "Nginx: Não respondeu"
    fi
}

# Limpeza
cleanup() {
    print_step "Limpando recursos..."
    
    # Parar containers
    docker-compose down 2>/dev/null || true
    docker-compose -f docker-compose.api.yml down 2>/dev/null || true
    
    # Limpar imagens não utilizadas
    docker image prune -f > /dev/null 2>&1 || true
    
    print_status "Limpeza concluída"
}

# Mostrar logs
show_logs() {
    print_step "Mostrando logs da aplicação..."
    
    if docker-compose ps | grep -q "Up"; then
        docker-compose logs -f --tail=50
    elif docker-compose -f docker-compose.api.yml ps | grep -q "Up"; then
        docker-compose -f docker-compose.api.yml logs -f --tail=50
    else
        print_warning "Nenhuma aplicação rodando"
    fi
}

# Mostrar status
show_status() {
    print_step "Status da aplicação..."
    
    echo ""
    print_info "📊 Containers:"
    docker-compose ps 2>/dev/null || docker-compose -f docker-compose.api.yml ps 2>/dev/null || echo "Nenhum container rodando"
    
    echo ""
    print_info "🐳 Imagens Docker:"
    docker images | grep $DOCKER_IMAGE || echo "Nenhuma imagem encontrada"
    
    echo ""
    print_info "💾 Volumes:"
    docker volume ls | grep $PROJECT_NAME || echo "Nenhum volume encontrado"
}

# Mostrar ajuda
show_help() {
    echo "🚀 Deploy Automatizado - Email Productivity Classifier"
    echo "=================================================="
    echo ""
    echo "Uso: $0 [OPÇÃO]"
    echo ""
    echo "Opções:"
    echo "  local        Deploy local (Streamlit + Nginx)"
    echo "  api          Deploy com API REST"
    echo "  prod         Deploy para produção (simulado)"
    echo "  cloud [aws|gcp|azure]  Deploy para cloud (simulado)"
    echo "  health       Verificar saúde da aplicação"
    echo "  logs         Mostrar logs"
    echo "  status       Mostrar status"
    echo "  clean        Limpar recursos"
    echo "  help         Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 local              # Deploy local"
    echo "  $0 api                # Deploy com API"
    echo "  $0 cloud aws          # Deploy para AWS"
    echo "  $0 health             # Health check"
    echo ""
}

# Função principal
main() {
    print_header "Email Productivity Classifier - Deploy Automatizado"
    echo "=================================================="
    
    # Verificar dependências
    check_docker
    check_git
    
    # Processar argumentos
    case $1 in
        "local")
            build_docker_image
            deploy_local
            health_check
            ;;
        "api")
            build_docker_image
            deploy_with_api
            health_check
            ;;
        "prod")
            build_docker_image
            deploy_production
            ;;
        "cloud")
            build_docker_image
            deploy_cloud $2
            ;;
        "health")
            health_check
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "clean")
            cleanup
            ;;
        "help"|"-h"|"--help"|"")
            show_help
            ;;
        *)
            print_error "Opção inválida: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
    
    echo ""
    print_status "Deploy concluído com sucesso!"
    print_info "Para mais informações, execute: $0 help"
}

# Executar função principal
main "$@"
