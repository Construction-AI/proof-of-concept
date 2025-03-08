package com.construction_ai.gateway.model;

import java.util.List;

import lombok.Data;

@Data
public class RouteDefinition {
    private String id;
    private String path;       
    private String serviceName;
    private List<String> methods;
}
