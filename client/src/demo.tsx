// Demo 模式 — 无需后端即可预览 UI
import React from 'react';

export const DEMO_MESSAGES = [
  {
    role: 'user' as const,
    content: '这份文档的主要内容是什么？',
  },
  {
    role: 'assistant' as const,
    content: '根据您上传的文档，主要包含以下几个方面的内容：\n\n1. **项目架构设计** — 采用微服务架构，包含用户服务、订单服务、商品服务等\n2. **技术栈选型** — 后端使用 Spring Boot，前端使用 React\n3. **数据库设计** — 使用 MySQL + Redis 缓存层\n\n文档还详细描述了每个模块的接口设计和数据流转过程。',
    sources: [
      { content: '1.2 系统架构 本系统采用微服务架构...', score: 0.95, source: '技术方案.pdf (第3页)' },
      { content: '3.1 数据库设计 使用 MySQL 8.0...', score: 0.87, source: '技术方案.pdf (第12页)' },
    ],
  },
  {
    role: 'user' as const,
    content: '性能方面有哪些优化措施？',
  },
  {
    role: 'assistant' as const,
    content: '文档中提到的性能优化措施包括：\n\n- **缓存策略**：使用 Redis 缓存热点数据，减少数据库查询\n- **连接池管理**：Druid 连接池，最大连接数 200\n- **异步处理**：订单处理采用消息队列异步化\n- **CDN 加速**：静态资源通过 CDN 分发\n\n预期 QPS 提升约 40%。',
    sources: [
      { content: '5.3 性能优化 在性能优化方面...', score: 0.92, source: '技术方案.pdf (第25页)' },
    ],
  },
];
