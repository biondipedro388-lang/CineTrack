from services.supabase_client import supabase

resposta = supabase.table("titulos").select("id").limit(1).execute()

print("Conexão com Supabase realizada!")
print(resposta.data)
