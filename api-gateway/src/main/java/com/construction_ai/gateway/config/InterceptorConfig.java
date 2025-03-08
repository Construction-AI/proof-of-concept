// package com.construction_ai.gateway.config;

// import org.springframework.beans.factory.annotation.Autowired;
// import org.springframework.context.annotation.Configuration;
// import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
// import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

// import com.construction_ai.gateway.interceptor.GatewayInterceptor;

// @Configuration
// public class InterceptorConfig implements WebMvcConfigurer {
// 	private final GatewayInterceptor gatewayInterceptor;

// 	@Autowired
// 	public InterceptorConfig(GatewayInterceptor gatewayInterceptor) {
// 		this.gatewayInterceptor = gatewayInterceptor;
// 	}

// 	@Override
// 	public void addInterceptors(InterceptorRegistry registry) {
// 		registry.addInterceptor(gatewayInterceptor).addPathPatterns("/**");
// 	}
// }
