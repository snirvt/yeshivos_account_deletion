from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase clients
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')

# Client for regular operations
supabase: Client = create_client(supabase_url, supabase_key)

# Admin client for user management
supabase_admin: Client = create_client(supabase_url, supabase_service_key)

@app.route('/')
def index():
    """Main account deletion page"""
    return render_template('index.html')

@app.route('/delete-account', methods=['POST'])
def delete_account():
    """Handle account deletion request"""
    try:
        email = request.form.get('email')

        if not email:
            flash('Email address is required', 'error')
            return redirect(url_for('index'))

        # Get user by email
        try:
            # List all users and find the one with matching email
            users_response = supabase_admin.auth.admin.list_users()
            target_user = None
            for user in users_response:
                if user.email == email:
                    target_user = user
                    break

            if not target_user:
                flash('No account found with this email address', 'error')
                return redirect(url_for('index'))

            user_id = target_user.id

        except Exception as e:
            logger.error(f"Error finding user: {str(e)}")
            flash('Error processing request. Please try again.', 'error')
            return redirect(url_for('index'))

        # Delete user data from custom tables
        # Replace 'profiles' with your actual table names
        try:
            # Example: Delete from profiles table
            supabase_admin.table('profiles').delete().eq('user_id', user_id).execute()

            # Add more table deletions as needed:
            # supabase_admin.table('user_posts').delete().eq('user_id', user_id).execute()
            # supabase_admin.table('user_settings').delete().eq('user_id', user_id).execute()

            logger.info(f"Deleted user data for user_id: {user_id}")

        except Exception as e:
            logger.error(f"Error deleting user data: {str(e)}")
            # Continue with auth deletion even if table deletion fails

        # Delete user from authentication
        try:
            supabase_admin.auth.admin.delete_user(user_id)
            logger.info(f"Deleted user auth for user_id: {user_id}")

        except Exception as e:
            logger.error(f"Error deleting user auth: {str(e)}")
            flash('Failed to delete account. Please contact support.', 'error')
            return redirect(url_for('index'))

        flash('Account deleted successfully. All your data has been removed.', 'success')
        return redirect(url_for('success'))

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/success')
def success():
    """Success page after account deletion"""
    return render_template('success.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


# Remove or comment out this section:
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)

# Add this for Vercel:
app = app  # This ensures the app is available for Vercel