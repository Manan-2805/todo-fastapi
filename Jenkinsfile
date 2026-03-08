pipeline {
    agent any

    environment {
        IMAGE_NAME = "todo-fastapi-devops"
    }

    stages {
        stage('Run Tests') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    pytest tests/ -v --junitxml=test-results.xml --cov=app --cov-report=xml --cov-report=html --cov-report=term
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                    publishHTML(target: [
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Code Coverage Report',
                        keepAll: true
                    ])
                }

                success {
                    echo "✅ All tests passed (21 tests: auth, CRUD, data isolation)"
                    script {
                        withCredentials([string(credentialsId: 'notification-recipient', variable: 'EMAIL')]) {
                            emailext(
                                subject: "✅ Tests PASSED - ${JOB_NAME} #${BUILD_NUMBER}",
                                body: """All tests passed successfully!

Test Summary:
- Authentication Tests: PASSED
- CRUD Operation Tests: PASSED
- User Data Isolation Tests: PASSED

View details: ${BUILD_URL}testReport/
Coverage report: ${BUILD_URL}Code_Coverage_Report/""",
                                to: EMAIL
                            )
                        }
                    }
                }

                failure {
                    echo "❌ Tests failed"
                    script {
                        withCredentials([string(credentialsId: 'notification-recipient', variable: 'EMAIL')]) {
                            emailext(
                                subject: "❌ Tests FAILED - ${JOB_NAME} #${BUILD_NUMBER}",
                                body: """Test suite failed!

Check which tests failed:
${BUILD_URL}testReport/

Console logs: ${BUILD_URL}console""",
                                to: EMAIL
                            )
                        }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                script {
                    def gitShort = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    def tag = "${env.BUILD_NUMBER}-${gitShort}"
                    echo "Building Docker images with tags: ${tag} and latest"
                    docker.build("${IMAGE_NAME}:${tag}")
                    docker.build("${IMAGE_NAME}:latest")
                }
            }
            post {
                success {
                    script {
                        withCredentials([string(credentialsId: 'notification-recipient', variable: 'EMAIL')]) {
                            emailext(
                                subject: "✅ Docker Image Built - ${JOB_NAME} #${BUILD_NUMBER}",
                                body: """Docker image built successfully!

Image tags:
- ${IMAGE_NAME}:${BUILD_NUMBER}-<git-hash>
- ${IMAGE_NAME}:latest

Ready for deployment.""",
                                to: EMAIL
                            )
                        }
                    }
                }

                failure {
                    script {
                        withCredentials([string(credentialsId: 'notification-recipient', variable: 'EMAIL')]) {
                            emailext(
                                subject: "❌ Docker Build Failed - ${JOB_NAME} #${BUILD_NUMBER}",
                                body: "Docker image build failed! Check logs: ${BUILD_URL}console",
                                to: EMAIL
                            )
                        }
                    }
                }
            }
        }

        stage('Security Scan & Smoke Test') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                script {
                    echo "🔍 Running security scan with Trivy..."
                    sh '''
                        # Install Trivy if not available
                        if ! command -v trivy &> /dev/null; then
                            wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
                            echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
                            sudo apt-get update
                            sudo apt-get install trivy -y
                        fi
                        
                        # Scan the Docker image
                        trivy image --severity HIGH,CRITICAL ${IMAGE_NAME}:latest
                    '''
                    
                    echo "🧪 Running smoke tests on container..."
                    sh '''
                        # Start container in background
                        docker run -d --name test-container -p 8001:8000 \
                            -e DATABASE_URL="sqlite:///./test.db" \
                            ${IMAGE_NAME}:latest
                        
                        # Wait for container to be ready
                        sleep 5

                        # Basic health check
                        curl -f http://localhost:8001/ || exit 1

                        # Cleanup
                        docker stop test-container
                        docker rm test-container
                    '''
                }
            }
            post {
                always {
                    echo "🧹 Cleaning up test containers..."
                    sh 'docker rm -f test-container || true'
                }
                success {
                    echo "✅ Security scan and smoke tests passed"
                }
                failure {
                    echo "❌ Security scan or smoke tests failed"
                }
            }
        }
    }

    // Global alerts after entire pipeline
    post {
        always {
            echo "Pipeline finished with result: ${currentBuild.result}"
        }

        success {
            script {
                withCredentials([string(credentialsId: 'notification-recipient', variable: 'EMAIL')]) {
                    emailext(
                        subject: "🚀 Pipeline SUCCESS - ${JOB_NAME} #${BUILD_NUMBER}",
                        body: "Everything passed! View: ${BUILD_URL}",
                        to: EMAIL
                    )
                }
            }
        }

        failure {
            script {
                withCredentials([string(credentialsId: 'notification-recipient', variable: 'EMAIL')]) {
                    emailext(
                        subject: "🔥 Pipeline FAILED - ${JOB_NAME} #${BUILD_NUMBER}",
                        body: "Check console: ${BUILD_URL}console",
                        to: EMAIL
                    )
                }
            }
        }

        fixed {
            script {
                withCredentials([string(credentialsId: 'notification-recipient', variable: 'EMAIL')]) {
                    emailext(
                        subject: "✅ Build FIXED!",
                        body: "Previous failure is now fixed.",
                        to: EMAIL
                    )
                }
            }
        }
    }
}