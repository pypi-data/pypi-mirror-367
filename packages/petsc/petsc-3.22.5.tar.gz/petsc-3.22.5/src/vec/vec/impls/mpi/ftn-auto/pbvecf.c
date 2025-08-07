#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* pbvec.c */
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

#include "petscvec.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define veccreatempiwitharray_ VECCREATEMPIWITHARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define veccreatempiwitharray_ veccreatempiwitharray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define veccreateghostwitharray_ VECCREATEGHOSTWITHARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define veccreateghostwitharray_ veccreateghostwitharray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecghostgetghostis_ VECGHOSTGETGHOSTIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecghostgetghostis_ vecghostgetghostis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define veccreateghost_ VECCREATEGHOST
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define veccreateghost_ veccreateghost
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecmpisetghost_ VECMPISETGHOST
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecmpisetghost_ vecmpisetghost
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define veccreateghostblockwitharray_ VECCREATEGHOSTBLOCKWITHARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define veccreateghostblockwitharray_ veccreateghostblockwitharray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define veccreateghostblock_ VECCREATEGHOSTBLOCK
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define veccreateghostblock_ veccreateghostblock
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  veccreatempiwitharray_(MPI_Fint * comm,PetscInt *bs,PetscInt *n,PetscInt *N, PetscScalar array[],Vec *vv, int *ierr)
{
CHKFORTRANNULLSCALAR(array);
PetscBool vv_null = !*(void**) vv ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vv);
*ierr = VecCreateMPIWithArray(
	MPI_Comm_f2c(*(comm)),*bs,*n,*N,array,vv);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vv_null && !*(void**) vv) * (void **) vv = (void *)-2;
}
PETSC_EXTERN void  veccreateghostwitharray_(MPI_Fint * comm,PetscInt *n,PetscInt *N,PetscInt *nghost, PetscInt ghosts[], PetscScalar array[],Vec *vv, int *ierr)
{
CHKFORTRANNULLINTEGER(ghosts);
CHKFORTRANNULLSCALAR(array);
PetscBool vv_null = !*(void**) vv ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vv);
*ierr = VecCreateGhostWithArray(
	MPI_Comm_f2c(*(comm)),*n,*N,*nghost,ghosts,array,vv);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vv_null && !*(void**) vv) * (void **) vv = (void *)-2;
}
PETSC_EXTERN void  vecghostgetghostis_(Vec X,IS *ghost, int *ierr)
{
CHKFORTRANNULLOBJECT(X);
PetscBool ghost_null = !*(void**) ghost ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ghost);
*ierr = VecGhostGetGhostIS(
	(Vec)PetscToPointer((X) ),ghost);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ghost_null && !*(void**) ghost) * (void **) ghost = (void *)-2;
}
PETSC_EXTERN void  veccreateghost_(MPI_Fint * comm,PetscInt *n,PetscInt *N,PetscInt *nghost, PetscInt ghosts[],Vec *vv, int *ierr)
{
CHKFORTRANNULLINTEGER(ghosts);
PetscBool vv_null = !*(void**) vv ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vv);
*ierr = VecCreateGhost(
	MPI_Comm_f2c(*(comm)),*n,*N,*nghost,ghosts,vv);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vv_null && !*(void**) vv) * (void **) vv = (void *)-2;
}
PETSC_EXTERN void  vecmpisetghost_(Vec vv,PetscInt *nghost, PetscInt ghosts[], int *ierr)
{
CHKFORTRANNULLOBJECT(vv);
CHKFORTRANNULLINTEGER(ghosts);
*ierr = VecMPISetGhost(
	(Vec)PetscToPointer((vv) ),*nghost,ghosts);
}
PETSC_EXTERN void  veccreateghostblockwitharray_(MPI_Fint * comm,PetscInt *bs,PetscInt *n,PetscInt *N,PetscInt *nghost, PetscInt ghosts[], PetscScalar array[],Vec *vv, int *ierr)
{
CHKFORTRANNULLINTEGER(ghosts);
CHKFORTRANNULLSCALAR(array);
PetscBool vv_null = !*(void**) vv ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vv);
*ierr = VecCreateGhostBlockWithArray(
	MPI_Comm_f2c(*(comm)),*bs,*n,*N,*nghost,ghosts,array,vv);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vv_null && !*(void**) vv) * (void **) vv = (void *)-2;
}
PETSC_EXTERN void  veccreateghostblock_(MPI_Fint * comm,PetscInt *bs,PetscInt *n,PetscInt *N,PetscInt *nghost, PetscInt ghosts[],Vec *vv, int *ierr)
{
CHKFORTRANNULLINTEGER(ghosts);
PetscBool vv_null = !*(void**) vv ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vv);
*ierr = VecCreateGhostBlock(
	MPI_Comm_f2c(*(comm)),*bs,*n,*N,*nghost,ghosts,vv);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vv_null && !*(void**) vv) * (void **) vv = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
