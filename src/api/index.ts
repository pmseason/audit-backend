import express from 'express';
import auditRouter from './audit';

const router = express.Router();

router.get('/', (req, res) => {
  res.json({
    message: "Server is Running"
  });
});

router.use('/audit', auditRouter);


export default router;
