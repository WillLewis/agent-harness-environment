'use client';

import { motion, useReducedMotion } from 'framer-motion';
import clsx from 'clsx';

type VerdictStampProps = {
  policyKey: string;
  verdict: 'accepted' | 'rejected' | 'assisted';
  label: string;
  reason: string;
};

function verdictTone(verdict: VerdictStampProps['verdict']) {
  if (verdict === 'rejected') {
    return {
      border: 'border-red-300/30 bg-red-300/10',
      stamp: 'text-red-100'
    };
  }
  if (verdict === 'assisted') {
    return {
      border: 'border-amber-300/30 bg-amber-300/10',
      stamp: 'text-amber-100'
    };
  }
  return {
    border: 'border-emerald-300/30 bg-emerald-300/10',
    stamp: 'text-emerald-100'
  };
}

export function VerdictStamp({ policyKey, verdict, label, reason }: VerdictStampProps) {
  const reduceMotion = useReducedMotion();
  const tone = verdictTone(verdict);

  return (
    <motion.div
      key={policyKey}
      initial={reduceMotion ? false : { opacity: 0, scale: 0.96, y: 8 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: reduceMotion ? 0 : 0.35, ease: 'easeOut' }}
      className={clsx('rounded-3xl border p-5', tone.border)}
    >
      <div className="text-xs uppercase tracking-[0.28em] text-slate-300">Verdict</div>
      <motion.div
        initial={reduceMotion ? false : { opacity: 0, scale: 1.08 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: reduceMotion ? 0 : 0.4, delay: reduceMotion ? 0 : 0.08 }}
        className={clsx('mt-2 text-2xl font-black tracking-tight', tone.stamp)}
      >
        {label}
      </motion.div>
      <p className="mt-3 text-sm leading-6 text-slate-200">{reason}</p>
    </motion.div>
  );
}
