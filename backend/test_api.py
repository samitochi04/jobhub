#!/usr/bin/env python3
"""
Script de test pour valider l'API JobHub
"""
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:5000"
API_URL = f"{BASE_URL}/api"

def test_health():
    """Test de l'endpoint de santé"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        print("✅ Health check passed")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_create_search():
    """Test de création d'une recherche"""
    print("🔍 Testing search creation...")
    try:
        payload = {
            "keywords": "python developer",
            "job_types": ["CDI", "freelance"],
            "platforms": ["indeed", "linkedin"],
            "duration_minutes": 20
        }
        
        response = requests.post(f"{API_URL}/search", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert 'search' in data
        search_id = data['search']['id']
        
        print(f"✅ Search created with ID: {search_id}")
        return search_id
    except Exception as e:
        print(f"❌ Search creation failed: {e}")
        return None

def test_get_searches():
    """Test de récupération des recherches"""
    print("🔍 Testing searches retrieval...")
    try:
        response = requests.get(f"{API_URL}/searches")
        assert response.status_code == 200
        data = response.json()
        assert 'searches' in data
        assert len(data['searches']) > 0
        
        print(f"✅ Found {len(data['searches'])} searches")
        return True
    except Exception as e:
        print(f"❌ Searches retrieval failed: {e}")
        return False

def test_get_jobs():
    """Test de récupération des offres"""
    print("🔍 Testing jobs retrieval...")
    try:
        response = requests.get(f"{API_URL}/jobs")
        assert response.status_code == 200
        data = response.json()
        assert 'jobs' in data
        
        print(f"✅ Found {len(data['jobs'])} jobs")
        return True
    except Exception as e:
        print(f"❌ Jobs retrieval failed: {e}")
        return False

def test_job_stats():
    """Test des statistiques"""
    print("🔍 Testing job statistics...")
    try:
        response = requests.get(f"{API_URL}/jobs/stats")
        assert response.status_code == 200
        data = response.json()
        assert 'stats' in data
        
        stats = data['stats']
        print(f"✅ Stats: {stats['total_jobs']} jobs, {stats['new_jobs']} new, {stats['active_searches']} active searches")
        return True
    except Exception as e:
        print(f"❌ Job stats failed: {e}")
        return False

def test_search_specific(search_id):
    """Test d'une recherche spécifique"""
    if not search_id:
        return False
        
    print(f"🔍 Testing specific search {search_id}...")
    try:
        response = requests.get(f"{API_URL}/search/{search_id}")
        assert response.status_code == 200
        data = response.json()
        assert 'search' in data
        assert data['search']['id'] == search_id
        
        print(f"✅ Search {search_id} details retrieved")
        return True
    except Exception as e:
        print(f"❌ Search {search_id} details failed: {e}")
        return False

def test_status():
    """Test du statut global"""
    print("🔍 Testing global status...")
    try:
        response = requests.get(f"{API_URL}/status")
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert 'stats' in data
        
        print(f"✅ Status: {data['status']}")
        return True
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False

def test_platforms():
    """Test de la liste des plateformes"""
    print("🔍 Testing platforms list...")
    try:
        response = requests.get(f"{API_URL}/jobs/platforms")
        assert response.status_code == 200
        data = response.json()
        assert 'platforms' in data
        
        print(f"✅ Found {len(data['platforms'])} platforms")
        return True
    except Exception as e:
        print(f"❌ Platforms list failed: {e}")
        return False

def test_mark_jobs_seen():
    """Test de marquage des offres comme vues"""
    print("🔍 Testing mark jobs as seen...")
    try:
        # D'abord récupérer une recherche
        response = requests.get(f"{API_URL}/searches?active_only=true")
        searches = response.json()['searches']
        
        if not searches:
            print("⚠️  No active searches found, skipping mark as seen test")
            return True
            
        search_id = searches[0]['id']
        payload = {"search_id": search_id}
        
        response = requests.post(f"{API_URL}/jobs/mark-seen", json=payload)
        assert response.status_code == 200
        
        print(f"✅ Jobs marked as seen for search {search_id}")
        return True
    except Exception as e:
        print(f"❌ Mark jobs as seen failed: {e}")
        return False

def run_all_tests():
    """Lance tous les tests"""
    print("🚀 Starting JobHub API Tests")
    print("=" * 50)
    
    results = []
    search_id = None
    
    # Tests de base
    results.append(("Health Check", test_health()))
    results.append(("Get Searches", test_get_searches()))
    results.append(("Get Jobs", test_get_jobs()))
    results.append(("Job Statistics", test_job_stats()))
    results.append(("Global Status", test_status()))
    results.append(("Platforms List", test_platforms()))
    
    # Test de création (peut échouer si limite atteinte)
    search_id = test_create_search()
    results.append(("Create Search", search_id is not None))
    
    # Tests dépendants
    results.append(("Search Details", test_search_specific(search_id)))
    results.append(("Mark Jobs Seen", test_mark_jobs_seen()))
    
    # Résultats
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20s} : {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print(f"⚠️  {total - passed} tests failed. Check the API server.")
    
    return passed == total

if __name__ == "__main__":
    # Vérifier que le serveur est accessible
    try:
        requests.get(BASE_URL, timeout=5)
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to {BASE_URL}")
        print("Make sure the Flask server is running with: python run.py")
        exit(1)
    
    # Lancer les tests
    success = run_all_tests()
    exit(0 if success else 1)
