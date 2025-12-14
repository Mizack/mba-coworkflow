#!/usr/bin/env python3
"""
Script para verificar o status dos serviços AWS do CoworkFlow
"""

import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError

def check_aws_credentials():
    """Verifica se as credenciais AWS estão configuradas"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ Credenciais AWS configuradas para: {identity['Arn']}")
        return True
    except NoCredentialsError:
        print("❌ Credenciais AWS não encontradas")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar credenciais: {e}")
        return False

def check_ecr_repositories():
    """Verifica se os repositórios ECR existem"""
    try:
        ecr = boto3.client('ecr', region_name='us-east-1')
        repos = ecr.describe_repositories()
        
        expected_repos = [
            'coworkflow/frontend',
            'coworkflow/api-gateway',
            'coworkflow/ms-usuarios',
            'coworkflow/ms-espacos',
            'coworkflow/ms-reservas',
            'coworkflow/ms-pagamentos',
            'coworkflow/ms-precos',
            'coworkflow/ms-checkin',
            'coworkflow/ms-notificacoes',
            'coworkflow/ms-financeiro',
            'coworkflow/ms-analytics'
        ]
        
        existing_repos = [repo['repositoryName'] for repo in repos['repositories']]
        
        print("\n📦 Status dos Repositórios ECR:")
        for repo in expected_repos:
            if repo in existing_repos:
                print(f"✅ {repo}")
            else:
                print(f"❌ {repo} - NÃO ENCONTRADO")
                
        return len([r for r in expected_repos if r in existing_repos]) == len(expected_repos)
        
    except Exception as e:
        print(f"❌ Erro ao verificar ECR: {e}")
        return False

def check_ecs_cluster():
    """Verifica se o cluster ECS existe e está ativo"""
    try:
        ecs = boto3.client('ecs', region_name='us-east-1')
        clusters = ecs.describe_clusters(clusters=['coworkflow-cluster'])
        
        if clusters['clusters']:
            cluster = clusters['clusters'][0]
            status = cluster['status']
            print(f"\n🚀 Cluster ECS: {cluster['clusterName']} - Status: {status}")
            
            if status == 'ACTIVE':
                print("✅ Cluster ECS está ativo")
                return True
            else:
                print("❌ Cluster ECS não está ativo")
                return False
        else:
            print("❌ Cluster ECS 'coworkflow-cluster' não encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar ECS: {e}")
        return False

def check_ecs_services():
    """Verifica o status dos serviços ECS"""
    try:
        ecs = boto3.client('ecs', region_name='us-east-1')
        
        services = [
            'frontend-service',
            'api-gateway-service',
            'ms-usuarios-service',
            'ms-espacos-service',
            'ms-reservas-service',
            'ms-pagamentos-service',
            'ms-precos-service',
            'ms-checkin-service',
            'ms-notificacoes-service',
            'ms-financeiro-service',
            'ms-analytics-service'
        ]
        
        print("\n🔧 Status dos Serviços ECS:")
        
        for service_name in services:
            try:
                service_info = ecs.describe_services(
                    cluster='coworkflow-cluster',
                    services=[service_name]
                )
                
                if service_info['services']:
                    service = service_info['services'][0]
                    status = service['status']
                    running = service['runningCount']
                    desired = service['desiredCount']
                    
                    if status == 'ACTIVE' and running == desired:
                        print(f"✅ {service_name}: {status} ({running}/{desired})")
                    else:
                        print(f"⚠️  {service_name}: {status} ({running}/{desired})")
                else:
                    print(f"❌ {service_name}: NÃO ENCONTRADO")
                    
            except Exception as e:
                print(f"❌ {service_name}: ERRO - {e}")
                
    except Exception as e:
        print(f"❌ Erro ao verificar serviços ECS: {e}")

def check_rds():
    """Verifica se o banco RDS está disponível"""
    try:
        rds = boto3.client('rds', region_name='us-east-1')
        instances = rds.describe_db_instances(DBInstanceIdentifier='coworkflow-db')
        
        if instances['DBInstances']:
            db = instances['DBInstances'][0]
            status = db['DBInstanceStatus']
            endpoint = db['Endpoint']['Address']
            
            print(f"\n🗄️  Banco RDS: {db['DBInstanceIdentifier']}")
            print(f"   Status: {status}")
            print(f"   Endpoint: {endpoint}")
            
            if status == 'available':
                print("✅ Banco RDS está disponível")
                return True
            else:
                print("❌ Banco RDS não está disponível")
                return False
        else:
            print("❌ Banco RDS 'coworkflow-db' não encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar RDS: {e}")
        return False

def check_load_balancer():
    """Verifica se o Load Balancer está ativo"""
    try:
        elb = boto3.client('elbv2', region_name='us-east-1')
        lbs = elb.describe_load_balancers()
        
        coworkflow_lb = None
        for lb in lbs['LoadBalancers']:
            if 'coworkflow' in lb['LoadBalancerName']:
                coworkflow_lb = lb
                break
        
        if coworkflow_lb:
            status = coworkflow_lb['State']['Code']
            dns_name = coworkflow_lb['DNSName']
            
            print(f"\n🌐 Load Balancer: {coworkflow_lb['LoadBalancerName']}")
            print(f"   Status: {status}")
            print(f"   DNS: {dns_name}")
            
            if status == 'active':
                print("✅ Load Balancer está ativo")
                print(f"🔗 Acesse sua aplicação em: http://{dns_name}")
                return True
            else:
                print("❌ Load Balancer não está ativo")
                return False
        else:
            print("❌ Load Balancer do CoworkFlow não encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar Load Balancer: {e}")
        return False

def main():
    print("🔍 Verificando status da infraestrutura AWS do CoworkFlow...\n")
    
    # Verificar credenciais
    if not check_aws_credentials():
        print("\n❌ Configure suas credenciais AWS antes de continuar")
        return
    
    # Verificar componentes
    ecr_ok = check_ecr_repositories()
    ecs_cluster_ok = check_ecs_cluster()
    check_ecs_services()  # Sempre mostra o status
    rds_ok = check_rds()
    lb_ok = check_load_balancer()
    
    # Resumo
    print("\n" + "="*50)
    print("📊 RESUMO:")
    print(f"ECR Repositories: {'✅' if ecr_ok else '❌'}")
    print(f"ECS Cluster: {'✅' if ecs_cluster_ok else '❌'}")
    print(f"RDS Database: {'✅' if rds_ok else '❌'}")
    print(f"Load Balancer: {'✅' if lb_ok else '❌'}")
    
    if all([ecr_ok, ecs_cluster_ok, rds_ok, lb_ok]):
        print("\n🎉 Infraestrutura está funcionando corretamente!")
    else:
        print("\n⚠️  Alguns componentes precisam de atenção")
        print("💡 Execute 'terraform apply' para corrigir problemas de infraestrutura")

if __name__ == "__main__":
    main()