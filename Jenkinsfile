pipeline {
    agent any

    // Registers the "GitHub hook trigger for GITScm polling" trigger.
    // Takes effect after the job has run once (click "Build Now" the first time).
    triggers {
        githubPush()
    }

    options {
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.COMMIT_MSG   = sh(script: 'git log -1 --pretty=%s', returnStdout: true).trim()
                    env.COMMIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    env.COMMIT_AUTHOR = sh(script: 'git log -1 --pretty=%an', returnStdout: true).trim()
                }
                echo "Building commit ${env.COMMIT_SHORT}: ${env.COMMIT_MSG}"
            }
        }

        stage('Environment') {
            steps {
                sh 'python3 --version'
            }
        }

        stage('Syntax Check') {
            steps {
                sh 'python3 -m py_compile calculator.py test_calculator.py'
            }
        }

        stage('Unit Tests') {
            steps {
                sh 'python3 -m unittest discover -v'
            }
        }
    }

    post {
        success {
            notifyWebex("✅ **BUILD SUCCESS** — ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
        failure {
            notifyWebex("❌ **BUILD FAILED** — ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
        unstable {
            notifyWebex("⚠️ **BUILD UNSTABLE** — ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
    }
}

def notifyWebex(String headline) {
    def msg = """${headline}
- Commit: `${env.COMMIT_SHORT ?: 'n/a'}` — ${env.COMMIT_MSG ?: 'n/a'}
- Author: ${env.COMMIT_AUTHOR ?: 'n/a'}
- Duration: ${currentBuild.durationString.replace(' and counting', '')}
- Console: ${env.BUILD_URL}console"""

    withCredentials([
        string(credentialsId: 'webex-bot-token', variable: 'WEBEX_TOKEN'),
        string(credentialsId: 'webex-room-id',   variable: 'WEBEX_ROOM')
    ]) {
        withEnv(["WEBEX_MSG=${msg}"]) {
            // Single-quoted so secrets are expanded by the shell, not Groovy.
            sh '''
                python3 -c 'import json,os; print(json.dumps({"roomId": os.environ["WEBEX_ROOM"], "markdown": os.environ["WEBEX_MSG"]}))' > webex_payload.json
                curl -sS -o /dev/null -w "Webex API HTTP status: %{http_code}\\n" \
                     -X POST https://webexapis.com/v1/messages \
                     -H "Authorization: Bearer $WEBEX_TOKEN" \
                     -H "Content-Type: application/json" \
                     -d @webex_payload.json
            '''
        }
    }
}
