import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  vus: 500,
  duration: '10s',
};

export default function () {
  const res = http.get(
    'http://host.docker.internal:8000/api/short-links/V9mc7v',
    {
      redirects: 0,
    }
  );

  check(res, {
    'status is 302': (r) => r.status === 302,
  });

  sleep(1);
}