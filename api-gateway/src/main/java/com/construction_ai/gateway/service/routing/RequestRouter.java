package com.construction_ai.gateway.service.routing;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.construction_ai.gateway.exception.RouteNotFoundException;
import com.construction_ai.gateway.model.RouteDefinition;
import org.springframework.util.PathMatcher;


import jakarta.servlet.http.HttpServletRequest;

import org.springframework.util.AntPathMatcher;

@Service
public class RequestRouter {
	private final RouteRegistry routeRegistry;
	private PathMatcher pathMatcher = new AntPathMatcher();

	@Autowired
	public RequestRouter(RouteRegistry routeRegistry) {
		this.routeRegistry = routeRegistry;
	}

	public RouteDefinition determineRoute(HttpServletRequest request) throws RouteNotFoundException {
		String path = request.getRequestURI();
		String method = request.getMethod();

		return routeRegistry.getRoutes().stream()
			.filter(route -> pathMatches(route.getPath(), path))
			.filter(route -> methodMatches(route.getMethods(), method))
			.findFirst()
			.orElseThrow(() -> new RouteNotFoundException("No route found for " + path));
	}

	private boolean pathMatches(String routePath, String requestPath) {
		return pathMatcher.match(routePath, requestPath);
	}

	private boolean methodMatches(List<String> routeMethods, String requestMethod) {
		return routeMethods == null || routeMethods.isEmpty() || routeMethods.contains(requestMethod);
	}


}