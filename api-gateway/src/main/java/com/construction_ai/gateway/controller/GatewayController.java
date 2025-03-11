package com.construction_ai.gateway.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import jakarta.servlet.http.HttpServletRequest;

public interface GatewayController {
	static final Logger logger = LoggerFactory.getLogger(GatewayController.class);
	public ResponseEntity<?> handleRequest(HttpServletRequest request);
}