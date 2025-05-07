{{/*
Expand the name of the chart.
*/}}
{{- define "iris-classifier.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "iris-classifier.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "iris-classifier.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "iris-classifier.labels" -}}
helm.sh/chart: {{ include "iris-classifier.chart" . }}
{{ include "iris-classifier.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "iris-classifier.selectorLabels" -}}
app.kubernetes.io/name: {{ include "iris-classifier.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Define the liveness probe
*/}}
{{- define "iris-classifier.livenessProbe" -}}
{{- if (get (get .Values "probes" | default dict) "liveness") }}
httpGet:
  path: {{ .Values.probes.liveness.path }}
  port: {{ .Values.probes.liveness.port }}
initialDelaySeconds: {{ .Values.probes.liveness.initialDelaySeconds }}
periodSeconds: {{ .Values.probes.liveness.periodSeconds }}
timeoutSeconds: {{ .Values.probes.liveness.timeoutSeconds }}
failureThreshold: {{ .Values.probes.liveness.failureThreshold }}
{{- else }}
httpGet:
  path: /api/v1/health
  port: {{ .Values.route.port }}
initialDelaySeconds: 30
periodSeconds: 30
timeoutSeconds: 5
failureThreshold: 3
{{- end }}
{{- end }}

{{/*
Define the readiness probe
*/}}
{{- define "iris-classifier.readinessProbe" -}}
{{- if (get (get .Values "probes" | default dict) "readiness") }}
httpGet:
  path: {{ .Values.probes.readiness.path }}
  port: {{ .Values.probes.readiness.port }}
initialDelaySeconds: {{ .Values.probes.readiness.initialDelaySeconds }}
periodSeconds: {{ .Values.probes.readiness.periodSeconds }}
timeoutSeconds: {{ .Values.probes.readiness.timeoutSeconds }}
failureThreshold: {{ .Values.probes.readiness.failureThreshold }}
{{- else }}
httpGet:
  path: /api/v1/health
  port: {{ .Values.route.port }}
initialDelaySeconds: 30
periodSeconds: 30
timeoutSeconds: 5
failureThreshold: 3
{{- end }}
{{- end }}

{{/*
Define the service configuration
*/}}
{{- define "iris-classifier.serviceConfig" -}}

{{- if .Values.route.type }}
type: {{ .Values.route.type }}
{{- else }}
type: ClusterIP
{{- end }}
selector:
  {{- include "iris-classifier.selectorLabels" . | nindent 2 }}
ports:
- port: {{ .Values.route.port }}
  targetPort: {{ .Values.route.port }}
  protocol: TCP
  name: http
{{- end }}

{{/*
Define the route basic configuration
*/}}
{{- define "iris-classifier.routeBasicConfig" }}
{{- if .Values.route.className }}
ingressClassName: {{ .Values.route.className }}
{{- else }}
ingressClassName: nginx
{{- end }}
rules:
  - {{- with .Values.route.host }} host: {{ . }}{{ end }}
    http:
      paths:
        {{- if .Values.route.paths }}
        {{- range .Values.route.paths }}
        - path: {{ . }}
          pathType: {{- if $.Values.route.pathType }} {{ $.Values.route.pathType }} {{- else }} ImplementationSpecific {{- end }}
          backend:
            service:
              name: {{ include "iris-classifier.fullname" $ }}
              port:
                number: {{ $.Values.route.port }}
        {{- end }}
        {{- else }}
        - path: /
          pathType: ImplementationSpecific
          backend:
            service:
              name: {{ include "iris-classifier.fullname" $ }}
              port:
                number: {{ $.Values.route.port }}
        {{- end }}
{{- end }}

{{/*
Define the route extra configuration
*/}}
{{- define "iris-classifier.routeExtraConfig" }}
{{- $route := .Values.route | default dict }}
{{- if (hasKey $route "annotations") }}
  {{- range $key, $val := $route.annotations }}
{{ $key }}: {{ $val | quote }}
  {{- end }}
{{- else }}
kubernetes.io/ingress.class: "nginx"
nginx.ingress.kubernetes.io/ssl-redirect: "false"
{{- end }}
{{- end }}

{{/*
Define storage configuration
*/}}
{{- define "iris-classifier.storageConfig" -}}
{{- if .Values.storage.accessModes }}
accessModes:
  {{- range .Values.storage.accessModes }}
  - {{ . }}
  {{- end }}
{{- else }}
accessModes:
  - ReadWriteOnce
{{- end }}
{{- if .Values.storage.storageClass }}
storageClassName: {{ .Values.storage.storageClass }}
{{- else }}
storageClassName: model-serving-wro
{{- end }}
resources:
  requests:
    storage: {{ .Values.storage.size }}
{{- end }}