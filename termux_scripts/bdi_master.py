import asyncio
import json
import time
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Any
import yaml
import os
from flask import Flask, jsonify, render_template_string

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
    """🧠 Real-time system state monitoring and understanding"""
    def __init__(self):
        self.beliefs = {
            'system_health': 100,
            'resource_usage': 0,
            'active_agents': [],
            'revenue_metrics': {},
            'cloud_status': {},
            'last_updated': None
        }

    async def update_beliefs(self):
        """Update system beliefs from multiple sources"""
        try:
            # Monitor local system
            self.beliefs['resource_usage'] = self._get_resource_usage()
            # Check cloud services status
            cloud_status = await self._check_cloud_services()
            self.beliefs['cloud_status'] = cloud_status
            # Update revenue metrics (placeholder)
            revenue_data = await self._fetch_revenue_metrics()
            self.beliefs['revenue_metrics'] = revenue_data
            self.beliefs['last_updated'] = datetime.now().isoformat()
            print(f"🧠 Beliefs Updated: {self.beliefs['system_health']}% System Health")
            return True
        except Exception as e:
            print(f"❌ Belief Update Error: {e}")
            return False

    def _get_resource_usage(self) -> float:
        """Get current resource usage (Termux-optimized)"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except ImportError:
            # Fallback for ultra-light environment
            return 5.0 # Minimal usage assumption

    async def _check_cloud_services(self) -> Dict:
        """Check status of all cloud services"""
        services = {
            'github_actions': await self._ping_github(),
            'vercel_api': await self._ping_vercel(),
            'supabase_db': await self._ping_supabase(),
            'huggingface': await self._ping_huggingface()
        }
        return services

    async def _ping_github(self) -> bool:
        """Check GitHub Actions availability"""
        try:
            response = requests.get('https://api.github.com/zen', timeout=5)
            return response.status_code == 200
        except:
            return False

    async def _ping_vercel(self) -> bool:
        """Check Vercel API availability"""
        try:
            response = requests.get('https://api.vercel.com/v2/user', timeout=5)
            return response.status_code in [200, 401] # 401 is OK (auth required)
        except:
            return False

    async def _ping_supabase(self) -> bool:
        """Check Supabase availability"""
        try:
            # Replace with your Supabase URL
            response = requests.get('https://supabase.com/api/health', timeout=5)
            return True # Assume healthy for demo
        except:
            return False

    async def _ping_huggingface(self) -> bool:
        """Check HuggingFace availability"""
        try:
            response = requests.get('https://huggingface.co/api/whoami', timeout=5)
            return response.status_code in [200, 401]
        except:
            return False

    async def _fetch_revenue_metrics(self) -> Dict:
        """Fetch current revenue metrics (placeholder)"""
        return {
            'current_month': 12500,
            'target': 50000,
            'growth_rate': 15.3,
            'active_streams': 7
        }

class DesireEngine:
    """🎯 Adaptive goal setting and optimization"""
    def __init__(self, belief_system: BeliefSystem):
        self.belief_system = belief_system
        self.current_desires = []
        self.goal_hierarchy = []

    async def generate_desires(self):
        """Generate new desires based on current beliefs"""
        beliefs = self.belief_system.beliefs
        new_desires = []

        # Revenue optimization desires
        revenue = beliefs['revenue_metrics'].get('current_month', 0)
        target = beliefs['revenue_metrics'].get('target', 50000)
        if revenue < target * 0.8: # Less than 80% of target
            new_desires.append({
                'type': 'revenue_optimization',
                'priority': 10,
                'target_increase': target - revenue,
                'strategy': 'aggressive_scaling'
            })

        # System optimization desires
        if beliefs['system_health'] < 90:
            new_desires.append({
                'type': 'system_optimization',
                'priority': 8,
                'target_health': 95,
                'actions': ['cleanup', 'resource_optimization']
            })

        # Cloud scaling desires
        if len(beliefs['active_agents']) < 5:
            new_desires.append({
                'type': 'agent_scaling',
                'priority': 6,
                'target_agents': 10,
                'deployment_strategy': 'gradual'
            })

        self.current_desires = new_desires
        print(f"🎯 Generated {len(new_desires)} desires")
        return new_desires

class IntentionSystem:
    """⚡ Action planning and execution coordination"""
    def __init__(self, belief_system: BeliefSystem, desire_engine: DesireEngine):
        self.belief_system = belief_system
        self.desire_engine = desire_engine
        self.active_intentions = []

    async def form_intentions(self):
        """Convert desires into actionable intentions"""
        desires = self.desire_engine.current_desires
        intentions = []
        for desire in desires:
            if desire['type'] == 'revenue_optimization':
                intentions.append({
                    'action': 'trigger_github_workflow',
                    'workflow': 'revenue-optimization.yml',
                    'parameters': {
                        'target_increase': desire['target_increase'],
                        'strategy': desire['strategy']
                    },
                    'priority': desire['priority']
                })
            elif desire['type'] == 'system_optimization':
                intentions.append({
                    'action': 'local_optimization',
                    'tasks': ['cleanup_logs', 'optimize_processes'],
                    'priority': desire['priority']
                })
            elif desire['type'] == 'agent_scaling':
                intentions.append({
                    'action': 'deploy_agents',
                    'platform': 'vercel',
                    'count': desire['count'],
                    'priority': desire['priority']
                })
        # Sort by priority (highest first)
        intentions.sort(key=lambda x: x['priority'], reverse=True)
        self.active_intentions = intentions
        print(f"⚡ Formed {len(intentions)} intentions")
        return intentions

    async def execute_intentions(self):
        """Execute top priority intentions"""
        for intention in self.active_intentions[:3]: # Execute top 3
            try:
                await self._execute_single_intention(intention)
                print(f"✅ Executed: {intention['action']}")
            except Exception as e:
                print(f"❌ Execution failed: {intention['action']} - {e}")

    async def _execute_single_intention(self, intention: Dict):
        """Execute a single intention"""
        if intention['action'] == 'trigger_github_workflow':
            await self._trigger_github_workflow(
                intention['workflow'],
                intention['parameters']
            )
        elif intention['action'] == 'local_optimization':
            await self._perform_local_optimization(intention['tasks'])
        elif intention['action'] == 'deploy_agents':
            await self._deploy_agents(intention)

    async def _trigger_github_workflow(self, workflow: str, params: Dict):
        """Trigger GitHub Actions workflow"""
        # Placeholder for actual GitHub API integration
        print(f"🔄 Triggering workflow: {workflow} with params: {params}")
        # Example: Call GitHub Actions API using requests
        # url = f'https://api.github.com/repos/{config.github.owner}/{config.github.repo}/actions/workflows/{workflow}/dispatches'
        # headers = {'Authorization': f'token {os.getenv("GITHUB_TOKEN")}', 'Accept': 'application/vnd.github.v3+json'}
        # payload = {'ref': 'main', 'inputs': params}
        # response = requests.post(url, headers=headers, json=payload)
        # if response.status_code == 204: print("Workflow triggered successfully")
        # else: print(f"Failed to trigger workflow: {response.status_code} - {response.text}")

    async def _perform_local_optimization(self, tasks: List[str]):
        """Perform local system optimization"""
        for task in tasks:
            if task == 'cleanup_logs':
                os.system('find ~/fmaa-bdi-enterprise -name "*.log" -delete 2>/dev/null || true')
                print("Logs cleaned up.")
            elif task == 'optimize_processes':
                print("🔧 Optimizing processes (placeholder)...")

    async def _deploy_agents(self, intention: Dict):
        """Deploy new micro-agents to Vercel"""
        print(f"🚀 Deploying {intention['count']} REAL agents to {intention['platform']}...")
        cfg = self.config
        token = cfg['secrets']['VERCEL_TOKEN']
        project_id = cfg['secrets']['VERCEL_PROJECT_ID']
        owner = cfg['cloud_services']['github']['owner']
        repo = cfg['cloud_services']['github']['repo']

        url = f"https://api.vercel.com/v13/deployments"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "name": f"fmaa-bdi-agent-v1",
            "projectId": project_id,
            "target": "production",
            "gitSource": {
                "type": "github",
                "repo": repo,
                "owner": owner,
                "ref": "main"
            }
        }
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: requests.post(url, headers=headers, json=payload, timeout=20))

            if response.status_code in [200, 201, 202]:
                print(f"✅ Vercel deployment triggered successfully! ID: {response.json().get('id')}")
            else:
                print(f"❌ Vercel deployment failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Vercel API Call Error: {e}")

class FMAABDIMaster:
    """🤖 Master BDI Agent Orchestrator"""
    def __init__(self):
        self.belief_system = BeliefSystem()
        self.desire_engine = DesireEngine(self.belief_system)
        self.intention_system = IntentionSystem(self.belief_system, self.desire_engine)
        self.running = False
        self.config = self._load_config()

        # Initialize Flask app for dashboard
        self.app = Flask(__name__)
        self._setup_dashboard_routes()

    def _load_config(self) -> Dict:
        """Load configuration from YAML"""
        config_path = os.path.expanduser('~/fmaa-bdi-enterprise/android-center/config.yaml')
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: config.yaml not found at {config_path}. Using default config.")
            return self._default_config()

    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'bdi_agent': {'name': 'FMAA-BDI-Master'},
            'revenue_targets': {'monthly_goal': 50000},
            'cloud_services': {
                'github': {'owner': 'your-github-username', 'repo': 'fmaa-bdi-enterprise'},
                'vercel': {'project': 'fmaa-api'},
                'supabase': {'url': 'https://your-project.supabase.co'},
                'huggingface': {'model_hub': 'huggingface.co'}
            }
        }

    async def bdi_cycle(self):
        """Main BDI reasoning cycle"""
        print("🔄 Starting BDI Cycle...")
        # 1. Update Beliefs
        await self.belief_system.update_beliefs()
        # 2. Generate Desires
        await self.desire_engine.generate_desires()
        # 3. Form Intentions
        await self.intention_system.form_intentions()
        # 4. Execute Intentions
        await self.intention_system.execute_intentions()
        print("✅ BDI Cycle Complete")

    async def run_agent(self):
        """Run the BDI agent continuously"""
        self.running = True
        print("🚀 FMAA BDI Master Agent Starting...")
        cycle_count = 0
        while self.running:
            try:
                cycle_count += 1
                print(f"\n🔄 BDI Cycle #{cycle_count}")
                await self.bdi_cycle()
                # Wait before next cycle (configurable)
                await asyncio.sleep(30) # 30-second cycles
            except KeyboardInterrupt:
                print("\n👋 Shutting down BDI Agent...")
                self.running = False
            except Exception as e:
                print(f"❌ Error in BDI cycle: {e}")
                await asyncio.sleep(10) # Wait before retry

    def _setup_dashboard_routes(self):
        """Setup Flask dashboard routes"""
        @self.app.route('/')
        def dashboard():
            return render_template_string(DASHBOARD_TEMPLATE,
                                        beliefs=self.belief_system.beliefs,
                                        desires=self.desire_engine.current_desires,
                                        intentions=self.intention_system.active_intentions,
                                        running=self.running)

        @self.app.route('/api/status')
        def api_status():
            return jsonify({
                'status': 'running' if self.running else 'stopped',
                'beliefs': self.belief_system.beliefs,
                'desires': len(self.desire_engine.current_desires),
                'intentions': len(self.intention_system.active_intentions)
            })

    def start_dashboard(self):
        """Start the dashboard server"""
        print("🌐 Starting dashboard at http://localhost:8080")
        # Use 0.0.0.0 to make it accessible from other devices on the network
        self.app.run(host='0.0.0.0', port=8080, debug=False)


if __name__ == '__main__':
    master_agent = FMAABDIMaster()

    # Run the BDI agent cycle in the background
    asyncio.create_task(master_agent.run_agent())

    # Start the Flask dashboard server
    master_agent.start_dashboard()


