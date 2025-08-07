#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* snesmfj.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscsnes.h"
#include "petscdm.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmffdcomputejacobian_ MATMFFDCOMPUTEJACOBIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmffdcomputejacobian_ matmffdcomputejacobian
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsnesmfgetsnes_ MATSNESMFGETSNES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsnesmfgetsnes_ matsnesmfgetsnes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsnesmfsetreusebase_ MATSNESMFSETREUSEBASE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsnesmfsetreusebase_ matsnesmfsetreusebase
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsnesmfgetreusebase_ MATSNESMFGETREUSEBASE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsnesmfgetreusebase_ matsnesmfgetreusebase
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatesnesmf_ MATCREATESNESMF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatesnesmf_ matcreatesnesmf
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matmffdcomputejacobian_(SNES snes,Vec x,Mat jac,Mat B,void*dummy, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(jac);
CHKFORTRANNULLOBJECT(B);
*ierr = MatMFFDComputeJacobian(
	(SNES)PetscToPointer((snes) ),
	(Vec)PetscToPointer((x) ),
	(Mat)PetscToPointer((jac) ),
	(Mat)PetscToPointer((B) ),dummy);
}
PETSC_EXTERN void  matsnesmfgetsnes_(Mat J,SNES *snes, int *ierr)
{
CHKFORTRANNULLOBJECT(J);
PetscBool snes_null = !*(void**) snes ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(snes);
*ierr = MatSNESMFGetSNES(
	(Mat)PetscToPointer((J) ),snes);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! snes_null && !*(void**) snes) * (void **) snes = (void *)-2;
}
PETSC_EXTERN void  matsnesmfsetreusebase_(Mat J,PetscBool *use, int *ierr)
{
CHKFORTRANNULLOBJECT(J);
*ierr = MatSNESMFSetReuseBase(
	(Mat)PetscToPointer((J) ),*use);
}
PETSC_EXTERN void  matsnesmfgetreusebase_(Mat J,PetscBool *use, int *ierr)
{
CHKFORTRANNULLOBJECT(J);
*ierr = MatSNESMFGetReuseBase(
	(Mat)PetscToPointer((J) ),use);
}
PETSC_EXTERN void  matcreatesnesmf_(SNES snes,Mat *J, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool J_null = !*(void**) J ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(J);
*ierr = MatCreateSNESMF(
	(SNES)PetscToPointer((snes) ),J);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! J_null && !*(void**) J) * (void **) J = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
