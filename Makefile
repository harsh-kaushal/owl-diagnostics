# Makefile
build:
	eval $$(minikube docker-env) && docker build -t owl-agent:latest ./core

setup:
	kubectl create secret generic owl-secrets --from-literal=OPENROUTER_API_KEY='$(KEY)'
	kubectl apply -f deploy/
	kubectl apply -f utilities/s3mock.yaml

test:
	kubectl apply -f utilities/buggy-app.yaml

clean:
	kubectl delete -f deploy/
	kubectl delete -f utilities/