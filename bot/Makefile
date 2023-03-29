.PHONY: all clean actions

## FLAGS:
# TODO: This is a hotfix while RASA don't solve dependencies issues.
PIP_FLAGS = --use-deprecated=legacy-resolver
LOG_LEVEL = -vv
RASA_ENDPOINTS = --endpoints 
ENDPOINTS = endpoints/endpoints.yml
RASA_CREDENTIALS = --credentials
CREDENTIALS = credentials/credentials.yml

clean:
	rm -rf graph.html results/ models/* *.db* .*tensorboard*

install:
	pip install --upgrade pip 						&& \
	pip install -r requirements.txt

# RASALIT
install-rasalit:
	pip install $(PIP_FLAGS) -r rasalit-requirements.txt

rasalit:
	python -m rasalit nlu-cluster --port 8501

# NLU
train-nlu:
	rasa train nlu \
		$(LOG_LEVEL)

# CORE
train:
	rasa train \
		$(LOG_LEVEL)

# TESTS
test:
	rasa test \
		--out results/

test-nlu:
	rasa test nlu \
		--out results/results-nlu-test

test-core:
	rasa test core \
		--fail-on-prediction-errors \
		--out results/results-core-test

# UTIL
interactive:
	rasa interactive

validate:
	rasa data validate \
		$(LOG_LEVEL)

visualize:
		rasa visualize \
			--out ./graph.html

tensor:
		tensorboard \
			-- bind_all \
			--logdir .

# CHAT
telegram:
	rasa run \
		-m models/ \
		$(LOG_LEVEL) \
		$(RASA_ENDPOINTS) $(ENDPOINTS) \
		$(RASA_CREDENTIALS)	credentials/telegram-credentials.yml \
		--port 5005 \

shell:
	rasa shell \
		-m models/ \
		$(LOG_LEVEL) \
		$(RASA_ENDPOINTS) $(ENDPOINTS) \
		--port 5006

webchat:
	rasa run \
		-m models/ \
		$(LOG_LEVEL) \
		$(RASA_ENDPOINTS) $(ENDPOINTS) \
		$(RASA_CREDENTIALS)	$(CREDENTIALS) \
		--cors '*' \
		--port 5007 


# ACTIONS
actions:
	rasa run actions \
		--actions actions \
		$(LOG_LEVEL)
