# Architecture Patterns

## 1. API Gateway → Lambda → DynamoDB

```mermaid
graph LR
    C[Client] --> APIGW[API Gateway]
    APIGW --> L[Lambda]
    L --> DDB[(DynamoDB)]
```

## 2. S3 → Lambda → SNS

```mermaid
graph LR
    U[User Upload] --> S3[(S3 Bucket)]
    S3 -->|ObjectCreated| L[Lambda]
    L --> SNS[SNS Topic]
    SNS --> E[Email / SMS Subscribers]
```

## 3. EventBridge → Lambda → SQS

```mermaid
graph LR
    EB[EventBridge Rule] --> L[Lambda]
    L --> SQS[SQS Queue]
    SQS --> W[Worker Lambda]
```

## 4. CloudWatch → Lambda

```mermaid
graph LR
    ALM[CloudWatch Alarm] --> L[Lambda Remediation]
    LOG[Log Subscription] --> L2[Lambda Log Processor]
```

## 5. Lambda → RDS

```mermaid
graph LR
    APIGW[API Gateway] --> L[Lambda in VPC]
    L --> PROXY[RDS Proxy]
    PROXY --> RDS[(RDS MySQL)]
```

## 6. Lambda → EC2

```mermaid
graph LR
    EB[EventBridge Schedule] --> L[Lambda]
    L --> EC2[Start / Stop EC2 Instances]
```

## 7. Lambda → Secrets Manager

```mermaid
graph LR
    L[Lambda] --> SM[Secrets Manager]
    SM --> L
    L --> RDS[(Database)]
```

## 8. Lambda → Parameter Store

```mermaid
graph LR
    L[Lambda] --> PS[SSM Parameter Store]
    PS --> L
    L --> APP[Application Logic]
```
