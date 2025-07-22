pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'
        TEST_ENV = 'dev'
        ALLURE_VERSION = '2.24.0'
        // 从Jenkins凭据中获取敏感信息
        GODGPT_USERNAME = credentials('godgpt-username')
        GODGPT_PASSWORD = credentials('godgpt-password')
    }
    
    parameters {
        choice(
            name: 'TEST_ENV',
            choices: ['dev', 'test', 'prod'],
            description: '选择测试环境'
        )
        choice(
            name: 'TEST_MARKERS',
            choices: ['all', 'smoke', 'regression', 'api'],
            description: '选择测试标记'
        )
        booleanParam(
            name: 'GENERATE_REPORT',
            defaultValue: true,
            description: '是否生成Allure报告'
        )
        booleanParam(
            name: 'PARALLEL_EXECUTION',
            defaultValue: false,
            description: '是否并行执行测试'
        )
        string(
            name: 'CUSTOM_ARGS',
            defaultValue: '',
            description: '自定义pytest参数'
        )
    }
    
    stages {
        stage('环境准备') {
            steps {
                script {
                    echo "开始准备测试环境..."
                    echo "测试环境: ${params.TEST_ENV}"
                    echo "测试标记: ${params.TEST_MARKERS}"
                    echo "并行执行: ${params.PARALLEL_EXECUTION}"
                    
                    // 设置环境变量
                    env.TEST_ENV = params.TEST_ENV
                    
                    // 验证Jenkins凭据
                    if (!env.GODGPT_USERNAME || !env.GODGPT_PASSWORD) {
                        error "Jenkins凭据未配置！请在Jenkins中配置 'godgpt-username' 和 'godgpt-password' 凭据"
                    }
                    
                    echo "认证凭据已配置"
                }
            }
        }
        
        stage('代码检出') {
            steps {
                checkout scm
            }
        }
        
        stage('Python环境设置') {
            steps {
                script {
                    // 检查Python版本
                    sh 'python3 --version'
                    
                    // 创建虚拟环境
                    sh 'python3 -m venv venv'
                    sh 'source venv/bin/activate && pip install --upgrade pip'
                    
                    // 安装依赖
                    sh 'source venv/bin/activate && pip install -r requirements.txt'
                    
                    // 验证关键依赖
                    sh '''
                        source venv/bin/activate
                        python -c "import pytest, requests, allure; print('关键依赖安装成功')"
                    '''
                }
            }
        }
        
        stage('Allure安装') {
            steps {
                script {
                    // 下载并安装Allure
                    sh '''
                        if [ ! -d "allure-${ALLURE_VERSION}" ]; then
                            echo "下载Allure ${ALLURE_VERSION}..."
                            wget -O allure-${ALLURE_VERSION}.zip https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.zip
                            unzip allure-${ALLURE_VERSION}.zip
                            echo "Allure安装完成"
                        else
                            echo "Allure已存在，跳过下载"
                        fi
                    '''
                    
                    // 设置Allure路径
                    env.PATH = "${env.PATH}:${WORKSPACE}/allure-${ALLURE_VERSION}/bin"
                    
                    // 验证Allure安装
                    sh 'allure --version'
                }
            }
        }
        
        stage('代码检查') {
            steps {
                script {
                    sh '''
                        source venv/bin/activate
                        echo "执行代码质量检查..."
                        python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
                        python -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
                        echo "代码检查完成"
                    '''
                }
            }
        }
        
        stage('运行测试') {
            steps {
                script {
                    // 构建测试命令
                    def test_cmd = "source venv/bin/activate && python -m pytest"
                    
                    // 根据测试标记过滤
                    if (params.TEST_MARKERS != 'all') {
                        test_cmd += " -m ${params.TEST_MARKERS}"
                    }
                    
                    // 添加Allure参数
                    test_cmd += " --alluredir=./allure-results --clean-alluredir"
                    
                    // 添加详细输出
                    test_cmd += " -v"
                    
                    // 并行执行（可选）
                    if (params.PARALLEL_EXECUTION) {
                        test_cmd += " -n auto"
                    }
                    
                    // 添加自定义参数
                    if (params.CUSTOM_ARGS) {
                        test_cmd += " ${params.CUSTOM_ARGS}"
                    }
                    
                    echo "执行测试命令: ${test_cmd}"
                    
                    // 执行测试
                    try {
                        sh test_cmd
                    } catch (Exception e) {
                        echo "测试执行失败: ${e.getMessage()}"
                        // 即使测试失败，也继续生成报告
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        
        stage('生成报告') {
            when {
                expression { params.GENERATE_REPORT == true }
            }
            steps {
                script {
                    // 生成Allure报告
                    sh '''
                        source venv/bin/activate
                        echo "生成Allure报告..."
                        allure generate allure-results -o allure-report --clean
                        echo "报告生成完成"
                    '''
                    
                    // 归档报告
                    archiveArtifacts artifacts: 'allure-report/**/*', fingerprint: true
                }
            }
        }
        
        stage('发布报告') {
            when {
                expression { params.GENERATE_REPORT == true }
            }
            steps {
                script {
                    // 发布Allure报告到Jenkins
                    allure([
                        includeProperties: false,
                        jdk: '',
                        properties: [],
                        reportBuildPolicy: 'ALWAYS',
                        results: [[path: 'allure-results']]
                    ])
                }
            }
        }
        
        stage('清理环境') {
            always {
                script {
                    echo "清理测试环境..."
                    // 清理虚拟环境
                    sh 'rm -rf venv'
                    
                    // 清理临时文件
                    sh 'rm -rf __pycache__'
                    sh 'find . -name "*.pyc" -delete'
                    sh 'rm -rf .pytest_cache'
                    
                    // 清理日志文件（如果存在）
                    sh 'rm -rf logs/*.log || true'
                    
                    echo "环境清理完成"
                }
            }
        }
    }
    
    post {
        always {
            script {
                // 发送通知
                if (currentBuild.result == 'SUCCESS') {
                    echo "✅ 测试执行成功！"
                } else if (currentBuild.result == 'FAILURE') {
                    echo "❌ 测试执行失败！"
                } else if (currentBuild.result == 'UNSTABLE') {
                    echo "⚠️ 测试执行不稳定！"
                } else {
                    echo "⏹️ 测试执行被中断！"
                }
                
                // 清理敏感信息
                env.GODGPT_USERNAME = null
                env.GODGPT_PASSWORD = null
            }
        }
        
        success {
            script {
                echo "🎉 所有测试通过！"
                // 可以在这里添加成功通知（邮件、钉钉等）
            }
        }
        
        failure {
            script {
                echo "💥 测试失败，请检查日志！"
                // 可以在这里添加失败通知
            }
        }
        
        unstable {
            script {
                echo "⚠️ 测试不稳定，请检查！"
                // 可以在这里添加不稳定通知
            }
        }
    }
} 