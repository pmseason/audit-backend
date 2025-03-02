import express from 'express';
import morgan from 'morgan';
import helmet from 'helmet';
import cors from 'cors';
import { configure } from '@pmseason/ai-job-scraper';

import * as middlewares from './middlewares';
import api from './api';

require('dotenv').config();

const app = express();
// https://github.com/websockets/ws/issues/1810
app.use(morgan('dev'));
app.use(helmet());
app.use(cors());
app.use(express.json());

app.use(api);

app.use(middlewares.notFound);
app.use(middlewares.errorHandler);

configure(process.env.FIRECRAWL_API_KEY!, process.env.OPENAI_API_KEY!);

export default app;
