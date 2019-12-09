int get_password() { 
    return 987654321;
}

int hash(int i) {
	int hash = 987654321;
	return (i+hash)%2^32;
}

int main(int argc, char *argv[]) {
  int tainted = get_password();
 
  return hash(tainted);
}

// TODO LIST:
// * Code examples where a static policy overtaints, and a dynamic policy wouldn't.
// * A hash function. A static policy would taint it. A dynamic policy could exclude it.
// * An array taint.