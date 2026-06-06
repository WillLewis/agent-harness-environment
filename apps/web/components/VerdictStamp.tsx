'use client';

import { motion, useReducedMotion } from 'framer-motion';
import clsx from 'clsx';
import { verdictPanelClass, verdictTextClass } from '../lib/statusStyles';

type VerdictStampProps = {
  policyKey: string;
  verdict: 'accepted' | 'rejected' | 'assisted';
  label: string;
  reason: string;
};

export function VerdictStamp({ policyKey, verdict, label, reason }: VerdictStampProps) {
  const reduceMotion = useReducedMotion();

  return (
    <motion.div
      key={policyKey}
      initial={reduceMotion ? false : { opacity: 0, scale: 0.96, y: 8 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: reduceMotion ? 0 : 0.35, ease: 'easeOut' }}
      className={clsx('rounded-card border p-4', verdictPanelClass(verdict))}
    >
      <div className="font-mono text-[10px] uppercase tracking-wider text-text-faint">Verdict</div>
      <motion.div
        initial={reduceMotion ? false : { opacity: 0, scale: 1.08 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: reduceMotion ? 0 : 0.4, delay: reduceMotion ? 0 : 0.08 }}
        className={clsx('mt-1.5 text-lg font-bold tracking-tight', verdictTextClass(verdict))}
      >
        {label}
      </motion.div>
      <p className="mt-2 break-words text-sm leading-relaxed text-text-muted">{reason}</p>
    </motion.div>
  );
}
