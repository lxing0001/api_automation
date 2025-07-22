pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'
        TEST_ENV = 'dev'
        ALLURE_VERSION = '2.24.0'
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
    }
    
    stages {
        stage('环境准备') {
            steps {
                script {
                    echo "开始准备测试环境..."
                    echo "测试环境: ${params.TEST_ENV}"
                    echo "测试标记: ${params.TEST_MARKERS}"
                    
                    // 设置环境变量
                    env.TEST_ENV = params.TEST_ENV
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
                }
            }
        }
        
        stage('Allure安装') {
            steps {
                script {
                    // 下载并安装Allure
                    sh '''
                        if [ ! -d "allure-${ALLURE_VERSION}" ]; then
                            wget -O allure-${ALLURE_VERSION}.zip https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.zip
                            unzip allure-${ALLURE_VERSION}.zip
                        fi
                    '''
                    
                    // 设置Allure路径
                    env.PATH = "${env.PATH}:${WORKSPACE}/allure-${ALLURE_VERSION}/bin"
                }
            }
        }
        
        stage('代码检查') {
            steps {
                script {
                    sh '''
                        source venv/bin/activate
                        python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
                        python -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
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
                    
                    // 添加其他参数
                    test_cmd += " --alluredir=./allure-results --clean-alluredir -v"
                    
                    // 并行执行（可选）
                    if (params.TEST_MARKERS == 'smoke') {
                        test_cmd += " -n auto"
                    }
                    
                    echo "执行测试命令: ${test_cmd}"
                    sh test_cmd
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
                        allure generate allure-results -o allure-report --clean
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
                    // 清理虚拟环境
                    sh 'rm -rf venv'
                    
                    // 清理临时文件
                    sh 'rm -rf __pycache__'
                    sh 'find . -name "*.pyc" -delete'
                }
            }
        }
    }
    
    post {
        always {
            script {
                // 发送通知
                if (currentBuild.result == 'SUCCESS') {
                    echo "测试执行成功！"
                } else if (currentBuild.result == 'FAILURE') {
                    echo "测试执行失败！"
                } else {
                    echo "测试执行被中断！"
                }
            }
        }
        
        success {
            script {
                // 成功时的处理
                echo "所有测试通过！"
            }
        }
        
        failure {
            script {
                // 失败时的处理
                echo "测试失败，请检查日志！"
            }
        }
        
        unstable {
            script {
                // 不稳定的处理
                echo "测试不稳定，请检查！"
            }
        }
    }
} 