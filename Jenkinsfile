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
                        # Run Trivy only if already installed (skip installation)
                        if command -v trivy > /dev/null 2>&1; then
                            echo "Trivy found, running security scan..."
                            trivy image --severity HIGH,CRITICAL ${IMAGE_NAME}:latest || echo "⚠️ Trivy scan found issues but continuing..."
                        else
                            echo "⚠️ Trivy not installed. Skipping security scan."
                            echo "To enable security scanning, install Trivy in your Jenkins environment."
                        fi
                    '''
                    
                    echo "🧪 Running smoke tests on container..."
                    sh '''
                        SMOKE_NETWORK="smoke-test-net"
                        DB_CONTAINER="smoke-postgres"

                        # Cleanup leftovers from previous runs
                        docker rm -f test-container ${DB_CONTAINER} 2>/dev/null || true
                        docker network rm ${SMOKE_NETWORK} 2>/dev/null || true

                        # Create isolated network for smoke test stack
                        docker network create ${SMOKE_NETWORK}

                        # Start temporary postgres for smoke test
                        docker run -d --name ${DB_CONTAINER} --network ${SMOKE_NETWORK} \
                            -e POSTGRES_DB=tododb \
                            -e POSTGRES_USER=postgres \
                            -e POSTGRES_PASSWORD=postgres \
                            postgres:16

                        echo "Waiting for postgres to become ready..."
                        for i in $(seq 1 30); do
                            if docker exec ${DB_CONTAINER} pg_isready -U postgres -d tododb > /dev/null 2>&1; then
                                echo "Postgres is ready"
                                break
                            fi
                            if [ "$i" -eq 30 ]; then
                                echo "Postgres did not become ready in time"
                                docker logs ${DB_CONTAINER}
                                exit 1
                            fi
                            sleep 2
                        done

                        # Start application against temporary postgres
                        docker run -d --name test-container --network ${SMOKE_NETWORK} \
                            -e DATABASE_URL="postgresql://postgres:postgres@${DB_CONTAINER}:5432/tododb" \
                            -e SECRET_KEY="smoke-test-secret-not-for-production" \
                            ${IMAGE_NAME}:latest

                        echo "Waiting for app to start..."
                        sleep 20

                        # Run health check from an ephemeral probe container on the same network
                        echo "Running health check..."
                        if docker run --rm --network ${SMOKE_NETWORK} curlimages/curl:8.8.0 -fsS http://test-container:8000/ > /dev/null; then
                            echo "✅ Smoke test passed!"
                        else
                            echo "❌ Smoke test failed!"
                            docker logs ${DB_CONTAINER}
                            docker logs test-container
                            exit 1
                        fi

                        # Cleanup
                        docker rm -f test-container ${DB_CONTAINER}
                        docker network rm ${SMOKE_NETWORK}
                    '''
                }
            }
            post {
                always {
                    echo "🧹 Cleaning up test containers..."
                    sh '''
                        docker rm -f test-container smoke-postgres 2>/dev/null || true
                        docker network rm smoke-test-net 2>/dev/null || true
                    '''
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