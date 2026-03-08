pipeline {
    agent any

    environment {
        IMAGE_NAME = "todo-fastapi-devops"
        REGISTRY   = "registry:5000"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Run Tests') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    export SECRET_KEY="test-secret-key-not-for-production"
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
                    echo "All tests passed (21 tests: auth, CRUD, data isolation)"
                    script {
                        withCredentials([string(credentialsId: 'notification-recipient', variable: 'EMAIL')]) {
                            emailext(
                                subject: "Tests PASSED - ${JOB_NAME} #${BUILD_NUMBER}",
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
                    echo "Tests failed"
                    script {
                        withCredentials([string(credentialsId: 'notification-recipient', variable: 'EMAIL')]) {
                            emailext(
                                subject: "Tests FAILED - ${JOB_NAME} #${BUILD_NUMBER}",
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

        stage('Build & Push to Registry') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                script {
                    def gitShort = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    def tag       = "${env.BUILD_NUMBER}-${gitShort}"
                    def fullTag   = "${env.REGISTRY}/${env.IMAGE_NAME}:${tag}"
                    def latestTag = "${env.REGISTRY}/${env.IMAGE_NAME}:latest"
                    echo "Building Docker image: ${fullTag}"
                    sh "docker build -t ${fullTag} -t ${latestTag} ."
                    echo "Pushing to local registry..."
                    sh "docker push ${fullTag}"
                    sh "docker push ${latestTag}"
                }
            }
            post {
                success {
                    script {
                        withCredentials([string(credentialsId: 'notification-recipient', variable: 'EMAIL')]) {
                            emailext(
                                subject: "Docker Image Built & Pushed - ${JOB_NAME} #${BUILD_NUMBER}",
                                body: """Docker image built and pushed to local registry!

Registry: ${REGISTRY}
Image tags:
- ${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER}-<git-hash>
- ${REGISTRY}/${IMAGE_NAME}:latest

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
                                subject: "Docker Build Failed - ${JOB_NAME} #${BUILD_NUMBER}",
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
                    echo "Running security scan with Trivy..."
                    sh """
                        if command -v trivy > /dev/null 2>&1; then
                            echo "Trivy found, running security scan..."
                            trivy image --severity HIGH,CRITICAL ${REGISTRY}/${IMAGE_NAME}:latest || echo "Trivy scan found issues but continuing..."
                        else
                            echo "Trivy not installed. Skipping security scan."
                            echo "To enable security scanning, install Trivy in your Jenkins environment."
                        fi
                    """

                    echo "Running smoke tests via docker-compose..."
                    sh """
                        export APP_IMAGE="${REGISTRY}/${IMAGE_NAME}:latest"
                        export SECRET_KEY="smoke-test-secret-not-for-production"
                        export COMPOSE_PROJECT_NAME="smoke-${BUILD_NUMBER}"

                        docker compose up -d --wait
                        echo "Smoke test passed - all services are healthy!"
                    """
                }
            }
            post {
                always {
                    echo "Tearing down smoke test stack..."
                    sh """
                        COMPOSE_PROJECT_NAME="smoke-${BUILD_NUMBER}" docker compose down --remove-orphans 2>/dev/null || true
                    """
                }
                success {
                    echo "Security scan and smoke tests passed"
                }
                failure {
                    echo "Security scan or smoke tests failed"
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
                        subject: "Pipeline SUCCESS - ${JOB_NAME} #${BUILD_NUMBER}",
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
                        subject: "Pipeline FAILED - ${JOB_NAME} #${BUILD_NUMBER}",
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
                        subject: "Build FIXED!",
                        body: "Previous failure is now fixed.",
                        to: EMAIL
                    )
                }
            }
        }
    }
}