pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'
        TEST_ENV = 'dev'
        ALLURE_VERSION = '2.24.0'
        LARK_WEBHOOK_URL = 'https://open.larksuite.com/open-apis/bot/v2/hook/a5fb88d3-c294-4fd3-be90-af3254f05b44'
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
                            # 检查是否已有Git仓库
                            if [ -d ".git" ]; then
                                echo "Git仓库已存在，检查远程配置..."
                                git remote -v
                                
                                # 如果远程仓库不存在或配置错误，重新配置
                                if ! git remote get-url origin >/dev/null 2>&1; then
                                    echo "添加远程仓库..."
                                    git remote add origin https://github.com/lxing0001/api_automation.git
                                else
                                    echo "远程仓库已配置"
                                fi
                                
                                # 拉取最新代码
                                echo "拉取最新代码..."
                                git fetch origin
                                git checkout main || git checkout master
                                git pull origin main || git pull origin master
                            else
                                echo "初始化Git仓库..."
                                git init
                                git remote add origin https://github.com/lxing0001/api_automation.git
                                git fetch origin
                                git checkout main || git checkout master
                            fi
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
                    
                    // 设置Allure工具路径供Jenkins插件使用
                    env.ALLURE_COMMAND = "${WORKSPACE}/allure-${ALLURE_VERSION}/bin/allure"
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
                
                // 发送飞书通知
                def status = currentBuild.result ?: 'SUCCESS'
                def statusText = ''
                def statusColor = ''
                
                switch(status) {
                    case 'SUCCESS':
                        statusText = '✅ 成功'
                        statusColor = '#00FF00'
                        break
                    case 'FAILURE':
                        statusText = '❌ 失败'
                        statusColor = '#FF0000'
                        break
                    case 'UNSTABLE':
                        statusText = '⚠️ 不稳定'
                        statusColor = '#FFA500'
                        break
                    default:
                        statusText = '⏹️ 中断'
                        statusColor = '#808080'
                }
                
                def message = [
                    msg_type: "interactive",
                    card: [
                        config: [
                            wide_screen_mode: true
                        ],
                        header: [
                            title: [
                                tag: "plain_text",
                                content: "GodGPT API巡检测试结果"
                            ],
                            template: statusColor
                        ],
                        elements: [
                            [
                                tag: "div",
                                text: [
                                    tag: "lark_md",
                                    content: "**项目名称**: GodGPT API自动化巡检项目\n**构建编号**: #${currentBuild.number}\n**构建状态**: ${statusText}\n**构建时间**: ${new Date().format('yyyy-MM-dd HH:mm:ss', TimeZone.getTimeZone('Asia/Shanghai'))}\n**构建时长**: ${currentBuild.durationString}"
                                ]
                            ],
                            [
                                tag: "div",
                                text: [
                                    tag: "lark_md",
                                    content: "**测试环境**: ${params.TEST_ENV}\n**测试标记**: ${params.TEST_MARKERS}\n"
                                ]
                            ],
                            [
                                tag: "action",
                                actions: [
                                    [
                                        tag: "button",
                                        text: [
                                            tag: "plain_text",
                                            content: "查看测试报告"
                                        ],
                                        type: "primary",
                                        url: "${env.BUILD_URL}artifact/allure-report/index.html"
                                    ]
                                ]
                            ]
                        ]
                    ]
                ]
                
                // 发送飞书通知
                try {
                    // 将消息转换为JSON字符串
                    def jsonMessage = groovy.json.JsonOutput.toJson(message)
                    
                    // 使用curl发送HTTP请求
                    def response = sh(
                        script: """
                            curl -X POST \\
                                -H 'Content-Type: application/json' \\
                                -d '${jsonMessage}' \\
                                '${env.LARK_WEBHOOK_URL}'
                        """,
                        returnStdout: true
                    ).trim()
                    
                    echo "飞书通知响应: ${response}"
                    echo "✅ 飞书通知发送成功"
                } catch (Exception e) {
                    echo "❌ 飞书通知发送异常: ${e.getMessage()}"
                }
                
                // 清理完成
            }
        }
        
        success {
            script {
                echo "🎉 所有测试通过！"
            }
        }
        
        failure {
            script {
                echo "💥 测试失败，请检查日志！"
            }
        }
        
        unstable {
            script {
                echo "⚠️ 测试不稳定，请检查！"
            }
        }
    }
} 