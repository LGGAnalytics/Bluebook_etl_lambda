FROM public.ecr.aws/lambda/python:3.11


# # Install Bash and other utilities
# RUN yum update -y && yum install -y bash

# Set the working directory
WORKDIR ${LAMBDA_TASK_ROOT}

RUN pip install --upgrade pip

# Copy and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all project files
COPY . .

# Define the command to run the main script
CMD [ "lambda_function.lambda_handler" ]

