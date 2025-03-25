{{/*
    Expand the name of the chart.
*/}}

{{- define "geocoding-helm.name" -}}
    {{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
    Create a default fully qualified app name.
    We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
    If release name contains chart name it will be used as a full name.
*/}}

{{- define "geocoding-helm.fullname" -}}
    {{- if .Values.fullnameOverride -}}
        {{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
    {{- else -}}
        {{- $name := default .Chart.Name .Values.nameOverride -}}
        {{- if contains $name .Release.Name -}}
            {{- .Release.Name | trunc 63 | trimSuffix "-" -}}
        {{- else -}}
            {{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
        {{- end -}}
    {{- end -}}
{{- end -}}

{{/*
    Create chart name and version as used by the chart label.
*/}}

{{- define "geocoding-helm.chart" -}}
    {{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
    Create the name of the service
*/}}
{{- define "geocoding-helm.servicename" -}}
    {{- if .Values.server.serviceName }}
        {{- .Values.server.serviceName -}}
    {{- else }}
        {{- printf "%s-server" (include "geocoding-helm.fullname" .) -}}
    {{- end -}}
{{- end -}}

{{/*
    Create the name of the service
*/}}
{{- define "geocoding-helm.fullservicename" -}}
    {{- if .Values.server.fullServiceName }}
        {{- printf "http://%s:80" .Values.server.fullServiceName -}}
    {{- else }}
        {{- printf "%s-server" (include "geocoding-helm.fullname" .) -}}
    {{- end -}}
{{- end -}}
