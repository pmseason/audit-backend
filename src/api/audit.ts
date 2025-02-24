import express from 'express';
import { MessageResponse } from '../types';
import { SearchConfig, SearchResult, startAudit } from '@mrinal-c/ai-job-scraper';


const router = express.Router();

type AuditInput = {
    remoteUrl: string;
    searchConfigs: SearchConfig[]
}

const clientMap = new Map<string, SearchResult[] | undefined>();

router.post('/start', (req, res) => {
    const { remoteUrl, searchConfigs } = req.body as AuditInput;

    // start audit
    const auditId = Math.random().toString(36).substring(7);

    // save client random id in client map
    clientMap.set(auditId, undefined);

    // start audit, once done set result in map
    startAudit(searchConfigs, remoteUrl).then((result) => {
        clientMap.set(auditId, result);
    }).catch((err) => {
        console.error(err);
    });

    // save client random id in cookie
    res.cookie('auditId', auditId);
    res.json({
        message: "Audit started",
    });
});

router.get('/:auditId', (req, res) => {
    // read client id from path
    const auditId = req.params.auditId;

    // get result from map
    const result = clientMap.get(auditId);

    if (result) {
        clientMap.delete(auditId);
        res.json(result);
    } else {
        res.status(404).json({
            message: "Invalid ID or Audit is in progress"
        } as MessageResponse);
    }
});

export default router;
