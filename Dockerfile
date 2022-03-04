FROM golang:1.13-alpine as builder
ARG VERSION=0.0.1

ENV GO111MODULE=on
ENV CGO_ENABLED=0
ENV GOOS=linux
ENV GOARCH=amd64



# build
WORKDIR /go/src/k8s-scheduler-extender-example
COPY go.mod .
COPY go.sum .
RUN GO111MODULE=on go mod download
COPY . .
RUN go install -ldflags "-s -w -X main.version=$VERSION" k8s-scheduler-extender-example

# runtime image
FROM gcr.io/google_containers/hyperkube:v1.16.3
# Image is stored from directory to container directory
COPY --from=builder /go/bin/k8s-scheduler-extender-example /usr/bin/k8s-scheduler-extender-example
#Integgrate File with scheduling data
COPY ./co2_prediction/average_co2_emissions.csv /usr/bin/average_co2_emissions.csv

ENTRYPOINT ["k8s-scheduler-extender-example"]
