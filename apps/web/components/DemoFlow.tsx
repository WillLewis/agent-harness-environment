'use client';

import { useCallback, useState } from 'react';
import { Cockpit } from './Cockpit';
import { TasksSection } from './TasksSection';
import { DEFAULT_TASK_ID, type TaskId } from '../lib/demoData';

export function DemoFlow() {
  const [activeTaskId, setActiveTaskId] = useState<TaskId>(DEFAULT_TASK_ID);
  const [autoplayToken, setAutoplayToken] = useState(0);

  const triggerTask = useCallback((taskId: TaskId) => {
    setActiveTaskId(taskId);
    setAutoplayToken((token) => token + 1);
    window.requestAnimationFrame(() => {
      document.getElementById('cockpit')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }, []);

  return (
    <>
      <TasksSection activeTaskId={activeTaskId} onTrigger={triggerTask} />
      <Cockpit activeTaskId={activeTaskId} onTaskChange={setActiveTaskId} autoplayToken={autoplayToken} />
    </>
  );
}
