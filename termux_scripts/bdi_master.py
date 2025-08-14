import asyncio
import json
import time
import requests
import subprocess
import threading
from datetime import datetime
from typing import Dict, List, Any
import yaml
import os
from flask import Flask, jsonify, render_template_string
from supabase import create_client, Client

# Template HTML untuk dashboard Flask
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FMAA BDI Agent Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }
        .container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1, h2 { color: #0056b3; }
        pre { background-color: #eee; padding: 10px; border-radius: 4px; overflow-x: auto; }
        .status-ok { color: green; font-weight: bold; }
        .status-error { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>FMAA BDI Agent Dashboard</h1>
        <p>Last Updated: {{ beliefs.last_updated }}</p>
        <h2>Beliefs (Current System State)</h2>
        <pre>{{ beliefs | tojson(indent=2) }}</pre>
        <h2>Desires (Goals)</h2>
        <pre>{{ desires | tojson(indent=2) }}</pre>
        <h2>Intentions (Actions)</h2>
        <pre>{{ intentions | tojson(indent=2) }}</pre>
        <h2>System Status</h2>
        <p>Running: <span class="{{ 'status-ok' if running else 'status-error' }}">{{ 'True' if running else 'False' }}</span></p>
    </div>
</body>
</html>
"""

class BeliefSystem:
    def __init__(self, config: Dict):
        self.config = config
        self.beliefs = {'system_health': 100, 'resource_usage': 0, 'active_agents': [], 'revenue_metrics': {}, 'cloud_status': {}, 'last_updated': None}

    async def update_beliefs(self):
        try:
            self.beliefs['resource_usage'] = self._get_resource_usage()
            self.beliefs['cloud_status'] = await self._check_cloud_services()
            self.beliefs['revenue_metrics'] = await self._fetch_revenue_metrics()
            self.beliefs['last_updated'] = datetime.now().isoformat()
            print(f"🧠 Beliefs Updated: {self.beliefs['system_health']}% System Health")
        except Exception as e: print(f"❌ Belief Update Error: {e}")

    def _get_resource_usage(self) -> float:
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            print(f"⚠️  Could not get CPU usage ({e}), using fallback.")
            return 5.0

    async def _check_cloud_services(self) -> Dict:
        return {'github_actions': await self._ping_github(), 'vercel_api': await self._ping_vercel(), 'supabase_db': await self._ping_supabase(), 'huggingface': await self._ping_huggingface()}

    async def _ping_github(self) -> bool:
        try:
            r = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.get('https://api.github.com/zen', timeout=5))
            return r.status_code == 200
        except: return False

    async def _ping_vercel(self) -> bool:
        try:
            r = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.get('https://api.vercel.com/v2/user', timeout=5))
            return r.status_code in [200, 401]
        except: return False

    async def _ping_supabase(self) -> bool:
        try:
            url = self.config['cloud_services']['supabase']['url']
            r = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.get(f"{url}/rest/v1/", headers={'apikey': self.config['secrets']['SUPABASE_KEY']}, timeout=5))
            return r.status_code in [200, 401, 404]
        except: return False

    async def _ping_huggingface(self) -> bool:
        try:
            r = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.get('https://huggingface.co/api/whoami', timeout=5))
            return r.status_code in [200, 401]
        except: return False

    async def _fetch_revenue_metrics(self) -> Dict:
        try:
            print("📊 Fetching REAL revenue metrics from Supabase...")
            cfg = self.config; url = cfg['cloud_services']['supabase']['url']; key = cfg['secrets']['SUPABASE_KEY']
            supabase: Client = create_client(url, key)
            response = supabase.table('revenue_metrics').select("*").limit(1).single().execute()
            data = response.data
            if data:
                data.pop('id', None); data.pop('name', None); data.pop('updated_at', None)
                print("✅ Real revenue data fetched."); return data
            else: raise Exception("No data found")
        except Exception as e:
            print(f"❌ Failed to fetch from Supabase: {e}. Using placeholder.")
            return {'current_month': 100, 'target': 50000, 'growth_rate': 0, 'active_streams': 0}

class DesireEngine:
    def __init__(self, belief_system: BeliefSystem):
        self.belief_system = belief_system; self.current_desires = []
    async def generate_desires(self):
        beliefs = self.belief_system.beliefs; new_desires = []
        revenue = beliefs['revenue_metrics'].get('current_month', 0); target = beliefs['revenue_metrics'].get('target', 50000)
        if revenue < target * 0.8: new_desires.append({'type': 'revenue_optimization', 'priority': 10, 'target_increase': target - revenue, 'strategy': 'aggressive_scaling'})
        if len(beliefs['active_agents']) < 5: new_desires.append({'type': 'agent_scaling', 'priority': 6, 'target_agents': 10, 'deployment_strategy': 'gradual'})
        self.current_desires = new_desires; print(f"🎯 Generated {len(new_desires)} desires")

class IntentionSystem:
    def __init__(self, belief_system: BeliefSystem, desire_engine: DesireEngine, config: Dict):
        self.belief_system = belief_system; self.desire_engine = desire_engine; self.config = config; self.active_intentions = []
    async def form_intentions(self):
        desires = self.desire_engine.current_desires; intentions = []
        for desire in desires:
            if desire['type'] == 'revenue_optimization': intentions.append({'action': 'trigger_github_workflow', 'workflow': 'bdi-action.yml', 'parameters': {'target_increase': str(desire['target_increase']), 'strategy': desire['strategy']}, 'priority': desire['priority']})
            elif desire['type'] == 'agent_scaling': intentions.append({'action': 'deploy_agents', 'platform': 'vercel', 'count': desire['target_agents'], 'priority': desire['priority']})
        intentions.sort(key=lambda x: x['priority'], reverse=True)
        self.active_intentions = intentions; print(f"⚡ Formed {len(intentions)} intentions")
    async def execute_intentions(self):
        for intention in self.active_intentions[:3]:
            try: await self._execute_single_intention(intention); print(f"✅ Executed: {intention['action']}")
            except Exception as e: print(f"❌ Execution failed: {intention['action']} - {e}")
    async def _execute_single_intention(self, intention: Dict):
        if intention['action'] == 'trigger_github_workflow': await self._trigger_github_workflow(intention['workflow'], intention['parameters'])
        elif intention['action'] == 'deploy_agents': await self._deploy_agents(intention)
    async def _trigger_github_workflow(self, workflow: str, params: Dict):
        print(f"🔄 Triggering REAL workflow: {workflow}")
        cfg = self.config; owner = cfg['cloud_services']['github']['owner']; repo = cfg['cloud_services']['github']['repo']; token = cfg['secrets']['GITHUB_TOKEN']
        url = f'https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow}/dispatches'; headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}; payload = {'ref': 'main', 'inputs': params}
        try:
            loop = asyncio.get_event_loop(); r = await loop.run_in_executor(None, lambda: requests.post(url, headers=headers, json=payload, timeout=10))
            if r.status_code == 204: print("✅ Workflow triggered successfully")
            else: print(f"❌ Failed to trigger workflow: {r.status_code} - {r.text}")
        except Exception as e: print(f"❌ API Call Error: {e}")
    async def _deploy_agents(self, intention: Dict):
        print(f"🚀 Deploying {intention['count']} REAL agents to {intention['platform']}...")
        cfg = self.config; token = cfg['secrets']['VERCEL_TOKEN']; project_id = cfg['secrets']['VERCEL_PROJECT_ID']; owner = cfg['cloud_services']['github']['owner']; repo = cfg['cloud_services']['github']['repo']
        url = f"https://api.vercel.com/v13/deployments"; headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {"name": f"fmaa-bdi-agent-v1", "projectId": project_id, "target": "production", "gitSource": {"type": "github", "repo": repo, "owner": owner, "ref": "main"}}
        try:
            loop = asyncio.get_event_loop(); r = await loop.run_in_executor(None, lambda: requests.post(url, headers=headers, json=payload, timeout=20))
            if r.status_code in [200, 201, 202]: print(f"✅ Vercel deployment triggered successfully! ID: {r.json().get('id')}")
            else: print(f"❌ Vercel deployment failed: {r.status_code} - {r.text}")
        except Exception as e: print(f"❌ Vercel API Call Error: {e}")

class FMAABDIMaster:
    def __init__(self):
        self.config = self._load_config()
        self.belief_system = BeliefSystem(self.config)
        self.desire_engine = DesireEngine(self.belief_system)
        self.intention_system = IntentionSystem(self.belief_system, self.desire_engine, self.config)
        self.running = False; self.app = Flask(__name__)
        self._setup_dashboard_routes()

    def _load_config(self) -> Dict:
        if os.getenv('VERCEL'):
            print("✅ Running on Vercel, using environment variables.")
            return {'cloud_services': {'github': {'owner': os.getenv('GITHUB_OWNER'), 'repo': os.getenv('GITHUB_REPO')},'supabase': {'url': os.getenv('SUPABASE_URL')}},'secrets': {'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),'SUPABASE_KEY': os.getenv('SUPABASE_KEY'),'VERCEL_TOKEN': os.getenv('VERCEL_TOKEN'),'VERCEL_PROJECT_ID': os.getenv('VERCEL_PROJECT_ID')},'revenue_targets': {'monthly_goal': 50000}}
        print("✅ Running locally, using config.yaml.")
        config_path = os.path.expanduser('~/fmaa-bdi-v1/android-center/config.yaml')
        try:
            with open(config_path, 'r') as f: return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"FATAL: config.yaml not found at {config_path}. Halting."); exit()

    async def run_agent(self):
        self.running = True; print("🚀 FMAA BDI Master Agent Starting..."); cycle_count = 0
        while self.running:
            try:
                cycle_count += 1; print(f"\n🔄 BDI Cycle #{cycle_count}"); await self.bdi_cycle(); await asyncio.sleep(30)
            except KeyboardInterrupt: print("\n👋 Shutting down BDI Agent..."); self.running = False
            except Exception as e: print(f"❌ Unhandled Error in BDI cycle: {e}"); await asyncio.sleep(10)

    def _setup_dashboard_routes(self):
        @self.app.route('/')
        def dashboard(): return render_template_string(DASHBOARD_TEMPLATE, beliefs=self.belief_system.beliefs, desires=self.desire_engine.current_desires, intentions=self.intention_system.active_intentions, running=self.running)
        @self.app.route('/api/status')
        def api_status(): return jsonify({'status': 'running' if self.running else 'stopped', 'beliefs': self.belief_system.beliefs, 'desires': len(self.desire_engine.current_desires), 'intentions': len(self.intention_system.active_intentions)})

    def start_dashboard(self):
        print("🌐 Starting dashboard at http://localhost:8080"); self.app.run(host='0.0.0.0', port=8080, debug=False)

    async def bdi_cycle(self):
        print("🔄 Starting BDI Cycle..."); await self.belief_system.update_beliefs(); await self.desire_engine.generate_desires(); await self.intention_system.form_intentions(); await self.intention_system.execute_intentions(); print("✅ BDI Cycle Complete")

master_agent = FMAABDIMaster()
app = master_agent.app

if __name__ == '__main__':
    print("🚀 Starting agent in local Termux mode...")
    dashboard_thread = threading.Thread(target=master_agent.start_dashboard, daemon=True)
    dashboard_thread.start()
    try:
        asyncio.run(master_agent.run_agent())
    except KeyboardInterrupt:
        print("\n👋 Agent dihentikan.")
