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
                    
                    echo "✅ 环境准备完成"
                }
            }
        }
        
        stage('代码检出') {
            steps {
                script {
                    echo "代码检出阶段..."
                    echo "当前工作目录: ${WORKSPACE}"
                    
                    // 检查当前目录内容
                    sh 'ls -la'
                    
                    // 对于自由风格项目，代码已经检出
                    // 对于Pipeline项目，使用checkout scm
                    try {
                        echo "尝试检出代码..."
                        checkout scm
                        echo "✅ 代码检出完成"
                    } catch (Exception e) {
                        echo "⚠️ 代码检出失败: ${e.getMessage()}"
                        echo "尝试手动检出代码..."
                        
                        // 手动检出代码
                        sh '''
                            git init
                            git remote add origin https://github.com/lxing0001/api_automation.git
                            git fetch origin
                            git checkout main
                        '''
                        echo "✅ 手动代码检出完成"
                    }
                    
                    // 验证文件是否存在
                    sh 'ls -la'
                    sh 'cat requirements.txt || echo "requirements.txt 不存在"'
                }
            }
        }
        
        stage('Python环境设置') {
            steps {
                script {
                    try {
                        // 检查Python版本
                        echo "检查Python版本..."
                        sh 'python3 --version'
                        
                        // 创建虚拟环境
                        echo "创建Python虚拟环境..."
                        sh 'python3 -m venv venv'
                        
                        // 升级pip
                        echo "升级pip..."
                        sh '. venv/bin/activate && pip install --upgrade pip'
                        
                        // 安装依赖
                        echo "安装Python依赖..."
                        echo "当前工作目录: ${WORKSPACE}"
                        sh 'ls -la'
                        sh '. venv/bin/activate && pip install -r requirements.txt'
                        
                        // 验证关键依赖
                        echo "验证关键依赖..."
                        sh '''
                            . venv/bin/activate
                            python -c "import pytest, requests, allure; print('关键依赖安装成功')"
                        '''
                        
                        echo "✅ Python环境设置完成"
                    } catch (Exception e) {
                        echo "❌ Python环境设置失败: ${e.getMessage()}"
                        error "Python环境设置失败，请检查Python安装和网络连接"
                    }
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
                        . venv/bin/activate
                        echo "执行代码质量检查..."
                        
                        # 检查flake8是否安装
                        if python -c "import flake8" 2>/dev/null; then
                            echo "flake8已安装，执行代码检查..."
                            python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
                            python -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
                        else
                            echo "⚠️ flake8未安装，跳过代码质量检查"
                            echo "请确保requirements.txt中包含flake8"
                        fi
                        
                        echo "代码检查完成"
                    '''
                }
            }
        }
        
        stage('运行测试') {
            steps {
                script {
                    // 构建测试命令
                    def test_cmd = ". venv/bin/activate && python -m pytest"
                    
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
                        . venv/bin/activate
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
            steps {
                script {
                    echo "清理测试环境..."
                    // 清理虚拟环境
                    sh 'rm -rf venv'
                    
                    // 清理临时文件
                    sh 'rm -rf __pycache__'
                    sh 'find . -name "*.pyc" -delete'
                    sh 'rm -rf .pytest_cache'
                    
                    // 清理日志文件（如果存在）
                    //sh 'rm -rf logs/*.log || true'
                    
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
                
                // 清理完成
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