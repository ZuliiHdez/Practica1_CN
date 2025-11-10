FROM public.ecr.aws/lambda/python:3.11

COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install -r requirements.txt

COPY lambdas/get_book/handler.py ${LAMBDA_TASK_ROOT}/
COPY app/ ${LAMBDA_TASK_ROOT}/app/

CMD [ "handler.lambda_handler" ]
